class Lamp {
  boolean isOn;
  Lamp() {
    isOn = false;
  }
  void turnOff() {
    isOn = false;
    System.out.println("Light on? " + isOn);
  }
}

class Main {
  public static void main(String[] args) {
    Lamp led = new Lamp();
    led.turnOff();
    led.turnOn();
  }
}
