package edu.gmu.argus.model;

public class Track {
	private String id;
	private double lat;
	private double lon;
	private double alt;
	private double gs;
	private double hdg;

	// Getters and setters
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public double getLat() {
		return lat;
	}

	public void setLat(double lat) {
		this.lat = lat;
	}

	public double getLon() {
		return lon;
	}

	public void setLon(double lon) {
		this.lon = lon;
	}

	public double getAlt() {
		return alt;
	}

	public void setAlt(double alt) {
		this.alt = alt;
	}

	public double getGs() {
		return gs;
	}

	public void setGs(double gs) {
		this.gs = gs;
	}

	public double getHdg() {
		return hdg;
	}

	public void setHdg(double hdg) {
		this.hdg = hdg;
	}

	@Override
	public String toString() {
		return "Track{" + "id='" + id + '\'' + ", lat=" + lat + ", lon=" + lon + ", alt=" + alt + ", gs=" + gs
				+ ", hdg=" + hdg + '}';
	}
}
