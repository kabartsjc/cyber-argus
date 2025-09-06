package edu.gmu.argus.cosim;

import org.springframework.web.bind.annotation.*;
import jakarta.annotation.PostConstruct;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/cosim")
public class CoSimController {

    private final Set<String> registeredFederates = new HashSet<>();
    private final Map<Integer, Set<String>> tickAcks = new ConcurrentHashMap<>();
    private int currentTime = 0;
    private final int federateJoinTimeoutSeconds = 15; // time to wait before simulation starts
    private Instant startTime;
    private boolean registrationWindowClosed = false;

    @PostConstruct
    public void init() {
        startTime = Instant.now();
        System.out.println("Server started. Waiting for federates to register...");
    }

    @PostMapping("/register")
    public String register(@RequestParam String name) {
        registeredFederates.add(name);
        System.out.println("Federate registered: " + name);
        return "Registered: " + name;
    }
    
    
    @PostMapping("/ack")
    public String ack(@RequestParam String name, @RequestParam int tick) {
        tickAcks.computeIfAbsent(tick, k -> new HashSet<>()).add(name);
        return "Ack received from " + name + " for tick " + tick;
    }

    @GetMapping("/tick")
    public synchronized Map<String, Object> tick() {
        Instant now = Instant.now();
        Set<String> currentAcks = tickAcks.getOrDefault(currentTime, new HashSet<>());
        System.out.println("Tick: " + currentTime + " ACKs so far: " + currentAcks);

        // Close registration window after timeout
        if (!registrationWindowClosed) {
            long elapsed = now.getEpochSecond() - startTime.getEpochSecond();
            if (elapsed >= federateJoinTimeoutSeconds) {
                registrationWindowClosed = true;
                System.out.println("Federate join window closed. Registered: " + registeredFederates);
            } else {
                return Map.of(
                    "time", currentTime,
                    "status", "waiting for federates to join",
                    "remaining", federateJoinTimeoutSeconds - elapsed
                );
            }
        }

        // Wait for all federates to acknowledge current tick
        if (!allAcknowledged(currentTime)) {
            return Map.of("time", currentTime, "status", "waiting for acknowledgments");
        }

        // Advance time
        currentTime++;
        tickAcks.put(currentTime, new HashSet<>());

        return Map.of("time", currentTime, "status", "ok");
    }

    @GetMapping("/federates")
    public Set<String> federates() {
        return registeredFederates;
    }

    private boolean allAcknowledged(int tick) {
        return tickAcks.getOrDefault(tick, new HashSet<>()).containsAll(registeredFederates);
    }
}

