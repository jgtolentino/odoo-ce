FROM quay.io/keycloak/keycloak:23.0 AS builder

# Enable health and metrics
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure database
ENV KC_DB=postgres

# Build optimized Keycloak
WORKDIR /opt/keycloak
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:23.0
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Set production mode
ENV KC_HOSTNAME_STRICT=false
ENV KC_PROXY=edge
ENV KC_HTTP_ENABLED=true

# Expose port
EXPOSE 8080

# Start Keycloak
ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
CMD ["start", "--optimized"]
