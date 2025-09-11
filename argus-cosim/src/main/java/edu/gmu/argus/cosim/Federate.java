package edu.gmu.argus.cosim;

import java.util.Collections;
import java.util.Set;
import java.util.concurrent.atomic.AtomicReference;

public class Federate {

    private final String id;
    private final String name;
    private final double lookahead;                // seconds
    private final Set<String> capabilities;        // e.g., ["state.publish","command.consume"]

    private final AtomicReference<Double> lastGrant   = new AtomicReference<>(0.0);
    private final AtomicReference<Double> lastRequest = new AtomicReference<>(0.0);

    private volatile FederateStatus status = FederateStatus.REGISTERED;
    private volatile long lastHeartbeatMs = System.currentTimeMillis();

    public Federate(String id, String name) {
        this(id, name, 0.1, Collections.emptySet());
    }

    public Federate(String id, String name, double lookahead, Set<String> capabilities) {
        this.id = id;
        this.name = name;
        this.lookahead = lookahead;
        this.capabilities = (capabilities == null) ? Collections.emptySet() : Set.copyOf(capabilities);
    }

    // --- Getters
    public String getId()                { return id; }
    public String getName()              { return name; }
    public double getLookahead()         { return lookahead; }
    public Set<String> getCapabilities() { return capabilities; }
    public double getLastGrant()         { return lastGrant.get(); }
    public double getLastRequest()       { return lastRequest.get(); }
    public FederateStatus getStatus()    { return status; }
    public long getLastHeartbeatMs()     { return lastHeartbeatMs; }

    // --- Updates
    public void updateRequest(double requestedTime) { lastRequest.set(requestedTime); }
    public void updateGrant(double grantedTime)     { lastGrant.set(grantedTime); status = FederateStatus.ACTIVE; }
    public void heartbeat()                         { lastHeartbeatMs = System.currentTimeMillis(); }
    public void markDisconnected()                  { status = FederateStatus.DISCONNECTED; }

    public boolean hasCapability(String cap)        { return capabilities.contains(cap); }

    @Override
    public String toString() {
        return "Federate{" +
               "id='" + id + '\'' +
               ", name='" + name + '\'' +
               ", lookahead=" + lookahead +
               ", lastGrant=" + lastGrant.get() +
               ", lastRequest=" + lastRequest.get() +
               ", status=" + status +
               '}';
    }

    public enum FederateStatus { REGISTERED, ACTIVE, DISCONNECTED }
}