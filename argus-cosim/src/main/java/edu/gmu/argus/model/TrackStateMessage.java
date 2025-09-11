package edu.gmu.argus.model;

import java.util.List;

public class TrackStateMessage {

	private String federateId;
	private double time;
	private List<Track> tracks;

	public String getFederateId() {
		return federateId;
	}

	public void setFederateId(String federateId) {
		this.federateId = federateId;
	}

	public double getTime() {
		return time;
	}

	public void setTime(double time) {
		this.time = time;
	}

	public List<Track> getTracks() {
		return tracks;
	}

	public void setTracks(List<Track> tracks) {
		this.tracks = tracks;
	}

}
