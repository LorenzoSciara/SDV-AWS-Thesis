package org.eclipse.hawkbit.simulator;

import org.eclipse.hawkbit.simulator.amqp.AmqpProperties;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {AmqpProperties.CONFIGURATION_ENABLED_PROPERTY + " = false"})
public abstract class DdiWebSecurityTest {

    @Autowired
    protected MockMvc mockMvc;

    static final String SIMULATOR_BASE_URL = "/";
    static final String SIMULATOR_BASE_URL_START = SIMULATOR_BASE_URL + "start?amount=5&api=ddi";

}
