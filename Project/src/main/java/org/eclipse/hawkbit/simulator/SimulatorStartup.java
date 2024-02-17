package org.eclipse.hawkbit.simulator;

import java.net.MalformedURLException;
import java.net.URL;

import org.eclipse.hawkbit.simulator.amqp.AmqpProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;

/**
 * Execution of operations after startup. Set up of simulations.
 *
 */
@Component
@ConditionalOnProperty(prefix = "hawkbit.device.simulator", name = "autostart", matchIfMissing = true)
public class SimulatorStartup implements ApplicationListener<ApplicationReadyEvent> {
    private static final Logger LOGGER = LoggerFactory.getLogger(SimulatorStartup.class);

    @Autowired
    private SimulationProperties simulationProperties;

    @Autowired
    private DeviceSimulatorRepository repository;

    @Autowired
    private SimulatedDeviceFactory deviceFactory;

    @Autowired
    private AmqpProperties amqpProperties;

    @Override
    public void onApplicationEvent(final ApplicationReadyEvent event) {
        LOGGER.debug("One autostarts will be executed");

        LOGGER.debug("Autostart runs for tenant {} and API {}", simulationProperties.getAutostarts().getTenant(), simulationProperties.getAutostarts().getApi());
        final String deviceId = simulationProperties.getAutostarts().getName(); //deviceId is the same of the autostart name
        try {
            if (amqpProperties.isEnabled()) {
                repository.add(deviceFactory.createSimulatedDeviceWithImmediatePoll(deviceId,
                        simulationProperties.getAutostarts().getTenant(), simulationProperties.getAutostarts().getApi(), simulationProperties.getAutostarts().getPollDelay(),
                        new URL(simulationProperties.getAutostarts().getEndpoint()), simulationProperties.getAutostarts().getGatewayToken()));
            }

        } catch (final MalformedURLException e) {
            LOGGER.error("Creation of simulated device at startup failed.", e);
        }
    }

}
