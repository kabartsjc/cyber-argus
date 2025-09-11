package edu.gmu.argus.cosim;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import edu.gmu.argus.model.Track;
import edu.gmu.argus.model.TrackStateMessage;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;

@RestController
@RequestMapping("/api/fed")
public class CoSimController {

	private final Map<String, Federate> fed = new ConcurrentHashMap<>();
	private final AtomicReference<Double> currentTime = new AtomicReference<>(0.0);
	// If you orchestrate multiple federates, gate grants until all are ready for
	// the next barrier.
	private final double lookahead = 0.1; // seconds
	private final double macroStep = 1.0; // grant in 1s slices, adjust as needed

	@PostMapping("/register")
	public Map<String, Object> register(@RequestBody Map<String, Object> req) {
		String name = (String) req.getOrDefault("name", "unnamed");
		String id = UUID.randomUUID().toString();
		fed.put(id, new Federate(id, name));
		return Map.of("federateId", id, "simStart", currentTime.get(), "simDt", 0.1);
	}

	@PostMapping("/requestTime")
	public synchronized Map<String, Object> requestTime(@RequestBody Map<String, Object> req) {
		String id = (String) req.get("federateId");
		double requestTime = ((Number) req.get("requestTime")).doubleValue();

		// Simple policy: grant at most currentTime + macroStep - lookahead
		double safeLimit = currentTime.get() + macroStep - lookahead;
		double grant = Math.min(requestTime, safeLimit);

		// Barrier: if you have N federates, track their lastGrant and only advance
		// currentTime when all have reached 'grant'. For a single federate, you can do:
		currentTime.set(Math.max(currentTime.get(), grant));
		fed.get(id).setLastGrant(grant);

		return Map.of("grantTime", grant);
	}

	@PostMapping("/trackstate")
	public ResponseEntity<Void> state(@RequestBody TrackStateMessage state) {
		System.out.println("Received state at time " + state.getTime() + " from federate " + state.getFederateId());

		for (Track track : state.getTracks()) {
			System.out.println(track);
		}

		return ResponseEntity.ok().build();
	}

	static class Federate {
		final String id;
		final String name;
		volatile double lastGrant = 0.0;

		Federate(String id, String name) {
			this.id = id;
			this.name = name;
		}

		void setLastGrant(double g) {
			this.lastGrant = g;
		}
	}
}