package org.eclipse.hawkbit.simulator.http;

import feign.RequestInterceptor;
import feign.RequestTemplate;

/**
 * A feign interceptor to apply the gateway-token header to each http-request.
 * 
 */
public class GatewayTokenInterceptor implements RequestInterceptor {

    private final String gatewayToken;

    /**
     * @param gatewayToken
     *            the gatwway token to be used in the http-header
     */
    public GatewayTokenInterceptor(final String gatewayToken) {
        this.gatewayToken = gatewayToken;
    }

    @Override
    public void apply(final RequestTemplate template) {
        template.header("Authorization", "GatewayToken " + gatewayToken);
    }
}
