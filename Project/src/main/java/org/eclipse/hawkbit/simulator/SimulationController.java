package org.eclipse.hawkbit.simulator;

import java.net.MalformedURLException;
import java.net.URL;
import java.util.Collections;
import java.util.Optional;

import org.eclipse.hawkbit.simulator.AbstractSimulatedDevice.Protocol;
import org.eclipse.hawkbit.simulator.amqp.AmqpProperties;
import org.eclipse.hawkbit.simulator.amqp.DmfSenderService;
import org.eclipse.hawkbit.simulator.amqp.SimulatedUpdate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST endpoint for controlling the device simulator.
 */
@RestController
public class SimulationController {

    private final DeviceSimulatorRepository repository;

    private final SimulatedDeviceFactory deviceFactory;

    private final AmqpProperties amqpProperties;

    private final SimulationProperties simulationProperties;

    private Optional<DmfSenderService> spSenderService = Optional.empty();

    @Autowired
    public SimulationController(final DeviceSimulatorRepository repository, final SimulatedDeviceFactory deviceFactory,
            final AmqpProperties amqpProperties, final SimulationProperties simulationProperties) {
        this.repository = repository;
        this.deviceFactory = deviceFactory;
        this.amqpProperties = amqpProperties;
        this.simulationProperties = simulationProperties;
    }

    /**
     * Simple endpoint indicating that simulator is running.
     */
    @GetMapping("/")
    public ResponseEntity<String> status() {
        return ResponseEntity.ok("Simulator running");
    }

    /**
     * The start resource to start a device creation.
     * 
     * @param name
     *            the name prefix of the generated device naming
     * @param amount
     *            the amount of devices to be created
     * @param tenant
     *            the tenant to create the device to
     * @param api
     *            the api-protocol to be used either {@code dmf} or {@code ddi}
     * @param endpoint
     *            the URL endpoint to be used of the hawkbit-update-server for
     *            DDI devices
     * @param pollDelay
     *            number of delay in seconds to delay polling of DDI devices
     * @param gatewayToken
     *            the hawkbit-update-server gatewaytoken in case authentication
     *            is enforced in hawkbit
     * @return a response string that devices has been created
     * @throws MalformedURLException
     */
    @GetMapping("/start")
    public ResponseEntity<String> start(@RequestParam(value = "name", defaultValue = "simulated") final String name,
            @RequestParam(value = "amount", defaultValue = "20") final int amount,
            @RequestParam(value = "tenant", required = false) final String tenant,
            @RequestParam(value = "api", defaultValue = "dmf") final String api,
            @RequestParam(value = "endpoint", defaultValue = "http://localhost:8080") final String endpoint,
            @RequestParam(value = "polldelay", defaultValue = "30") final int pollDelay,
            @RequestParam(value = "gatewaytoken", defaultValue = "") final String gatewayToken)
            throws MalformedURLException {

        final Protocol protocol;
        switch (api.toLowerCase()) {
        case "dmf":
            protocol = Protocol.DMF_AMQP;
            break;
        case "ddi":
            protocol = Protocol.DDI_HTTP;
            break;
        default:
            return ResponseEntity.badRequest().body("query param api only allows value of 'dmf' or 'ddi'");
        }

        if (protocol == Protocol.DMF_AMQP && isDmfDisabled()) {
            return createAmqpDisabledResponse();
        }

        for (int i = 0; i < amount; i++) {
            final String deviceId = name + i;
            repository.add(deviceFactory.createSimulatedDeviceWithImmediatePoll(deviceId,
                    (tenant != null ? tenant : simulationProperties.getDefaultTenant()), protocol, pollDelay,
                    new URL(endpoint), gatewayToken));
        }

        return ResponseEntity.ok("Updated " + amount + " " + protocol + " connected targets!");
    }

    private ResponseEntity<String> createAmqpDisabledResponse() {
        return ResponseEntity.badRequest().body(
                "The AMQP interface has been disabled, to use DMF protocol you need to enable the AMQP interface via '"
                        + AmqpProperties.CONFIGURATION_PREFIX + ".enabled=true'");
    }

    /**
     * Update an attribute of a device.
     *
     * NOTE: This represents not the expected client behaviour for DDI, since a
     * DDI client shall only update its attributes if requested by hawkBit.
     *
     * @param tenant
     *            The tenant the device belongs to
     * @param controllerId
     *            The controller id of the device that should be updated.
     * @param mode
     *            Update mode ('merge', 'replace', or 'remove')
     * @param key
     *            Key of the attribute to be updated
     * @param value
     *            Value of the attribute
     * @return HTTP OK (200) if the update has been triggered.
     */
    @GetMapping("/attributes")
    public ResponseEntity<String> update(@RequestParam(value = "tenant", required = false) final String tenant,
            @RequestParam(value = "controllerid") final String controllerId,
            @RequestParam(value = "mode", defaultValue = "merge") final String mode,
            @RequestParam(value = "key") final String key,
            @RequestParam(value = "value", required = false) final String value) {

        final AbstractSimulatedDevice simulatedDevice = repository
                .get((tenant != null ? tenant : simulationProperties.getDefaultTenant()), controllerId);

        if (simulatedDevice == null) {
            return ResponseEntity.notFound().build();
        }

        simulatedDevice.updateAttribute(mode, key, value);

        return ResponseEntity.ok("Update triggered");
    }

    /**
     * Remove a simulated device
     *
     * @param tenant
     *            The tenant the device belongs to
     * @param controllerId
     *            The controller id of the device that should be removed.
     * @return HTTP OK (200) if the device was removed, or HTTP NO FOUND (404)
     *         if not found.
     */
    @GetMapping("/remove")
    public ResponseEntity<String> remove(@RequestParam(value = "tenant", required = false) final String tenant,
            @RequestParam(value = "controllerid") final String controllerId) {

        final AbstractSimulatedDevice controller = repository
                .remove((tenant != null ? tenant : simulationProperties.getDefaultTenant()), controllerId);

        if (controller == null) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok("Deleted");
    }

    /**
     * Reset the device simulator by removing all simulated devices
     * 
     * @return A response string that the simulator has been reset
     */
    @GetMapping("/reset")
    public ResponseEntity<String> reset() {

        repository.clear();

        return ResponseEntity.ok("All simulated devices have been removed.");
    }

    /**
     * Report action as FINISHED Sends an UpdateActionStatus event with value
     * FINISHED
     *
     * @return A response string that the action_finished event was sent
     */
    @GetMapping("/finishAction")
    public ResponseEntity<String> finishAction(@RequestParam(value = "actionId") final long actionId,
            @RequestParam(value = "tenant", required = false) final String tenant,
            @RequestParam(value = "controllerId") final String controllerId) {

        if (!spSenderService.isPresent()) {
            return createAmqpDisabledResponse();
        }

        final String theTenant = tenant != null && !tenant.isEmpty() ? tenant : simulationProperties.getDefaultTenant();
        final AbstractSimulatedDevice device = repository.get(theTenant, controllerId);

        if (device == null) {
            return ResponseEntity.notFound().build();
        }

        spSenderService.get().finishUpdateProcess(new SimulatedUpdate(device.getTenant(), device.getId(), actionId),
                Collections.singletonList("Simulation Finished."));

        return ResponseEntity.ok(String.format("Action with id: [%d] reported as FINISHED", actionId));
    }

    @Autowired(required = false)
    public void setSpSenderService(final DmfSenderService spSenderService) {
        this.spSenderService = Optional.of(spSenderService);
    }

    private boolean isDmfDisabled() {
        return !amqpProperties.isEnabled();
    }
}
