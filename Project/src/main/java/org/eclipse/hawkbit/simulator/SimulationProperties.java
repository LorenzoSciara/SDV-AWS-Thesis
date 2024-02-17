package org.eclipse.hawkbit.simulator;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.concurrent.TimeUnit;

import javax.validation.constraints.NotEmpty;

import org.eclipse.hawkbit.simulator.AbstractSimulatedDevice.Protocol;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import com.google.common.base.Splitter;

/**
 * General simulator service properties.
 *
 */
@Component
@ConfigurationProperties("hawkbit.device.simulator")
// Exception for squid:S2245 : not security relevant random number generation
@SuppressWarnings("squid:S2245")
public class SimulationProperties {
    private static final Splitter SPLITTER = Splitter.on(',').omitEmptyStrings().trimResults();
    private static final Random RANDOM = new Random();

    private String defaultTenant = "DEFAULT";

    /**
     * Set to <code>true</code> if the target or gateway auth token should be
     * added to the download request as an authorization header. Activated by
     * default but may be worth to disable if not needed.
     */
    private boolean downloadAuthenticationEnabled = true;

    /**
     * List of tenants where the simulator should auto start simulations after
     * startup.
     */
    private final Autostart autostarts = new Autostart();

    private final List<Attribute> attributes = new ArrayList<>();

    public String getDefaultTenant() {
        return defaultTenant;
    }

    public void setDefaultTenant(final String defaultTenant) {
        this.defaultTenant = defaultTenant;
    }

    public boolean isDownloadAuthenticationEnabled() {
        return downloadAuthenticationEnabled;
    }

    public void setDownloadAuthenticationEnabled(final boolean downloadAuthenticationEnabled) {
        this.downloadAuthenticationEnabled = downloadAuthenticationEnabled;
    }

    public List<Attribute> getAttributes() {
        return attributes;
    }

    public Autostart getAutostarts() {
        return this.autostarts;
    }

    /**
     * Properties for target attributes set as part of simulation.
     *
     */
    public static class Attribute {
        private String key;
        private String value;
        private String random;

        public String getKey() {
            return key;
        }

        public String getValue() {
            return Optional.ofNullable(value).orElseGet(this::getRandomElement);
        }

        public void setKey(final String key) {
            this.key = key;
        }

        public void setValue(final String value) {
            this.value = value;
        }

        public void setRandom(final String random) {
            this.random = random;
        }

        public String getRandom() {
            return random;
        }

        private String getRandomElement() {
            final List<String> options = SPLITTER.splitToList(random);
            return options.get(RANDOM.nextInt(options.size()));
        }
    }

    /**
     * Auto start configuration for simulation setups that the simulator begins
     * after startup.
     *
     */
    public static class Autostart {
        /**
         * Name prefix of simulated devices, followed by counter, e.g.
         * simulated0, simulated1, simulated2....
         */
        private String name = "HawkbitDevice001"; //name of the device

        /**
         * Amount of simulated devices.
         */
        private int amount = 1; //number of the device

        /**
         * Tenant name for the simulation.
         */
        @NotEmpty
        private String tenant = "DEFAULT";

        /**
         * API for simulation.
         */
        private Protocol api = Protocol.DMF_AMQP;

        /**
         * Endpoint in case of DDI API based simulation.
         */
        private String endpoint = "http://localhost:8080";

        /**
         * Poll time in {@link TimeUnit#SECONDS} for simulated devices.
         */
        private int pollDelay = (int) TimeUnit.MINUTES.toSeconds(30);

        /**
         * Optional gateway token for DDI API based simulation.
         */
        private String gatewayToken = "";

        public String getName() {
            return name;
        }

        public void setName(final String name) {
            this.name = name;
        }

        public int getAmount() {
            return amount;
        }

        public void setAmount(final int amount) {
            this.amount = amount;
        }

        public String getTenant() {
            return tenant;
        }

        public void setTenant(final String tenant) {
            this.tenant = tenant;
        }

        public Protocol getApi() {
            return api;
        }

        public void setApi(final Protocol api) {
            this.api = api;
        }

        public String getEndpoint() {
            return endpoint;
        }

        public void setEndpoint(final String endpoint) {
            this.endpoint = endpoint;
        }

        public int getPollDelay() {
            return pollDelay;
        }

        public void setPollDelay(final int pollDelay) {
            this.pollDelay = pollDelay;
        }

        public String getGatewayToken() {
            return gatewayToken;
        }

        public void setGatewayToken(final String gatewayToken) {
            this.gatewayToken = gatewayToken;
        }
    }
}
