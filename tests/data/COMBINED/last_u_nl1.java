public class test {
protected Earth getEarth() {
    switch (earthShape) {
      case 0:
        return new Earth(6367470.0);
      case 1:
        if (earthRadius < 6000000) earthRadius *= 1000.0; // bad units
        return new Earth(earthRadius);
      case 2:
        return EarthEllipsoid.IAU;
      case 3:
        // oblate in km, so bad values will be large and not scaled
        if (majorAxis < 6000000) majorAxis *= 1000.0;
        if (minorAxis < 6000000) minorAxis *= 1000.0;
        return new EarthEllipsoid("Grib2 Type 3", -1, majorAxis, minorAxis, 0);
      case 4:
        return EarthEllipsoid.IAG_GRS80;
      case 5:
        return EarthEllipsoid.WGS84;
      case 6:
        return new Earth(6371229.0);
      case 7: // Oblate in meters
        if (majorAxis < 6000000) majorAxis *= 1000.0; // bad units
        if (minorAxis < 6000000) minorAxis *= 1000.0; // bad units
        return new EarthEllipsoid("Grib2 Type 7", -1, majorAxis, minorAxis, 0);
      case 8:
        return new Earth(6371200.0);
      case 9:
        return EarthEllipsoid.Airy1830;
      default:
        return new Earth();
    }
  }
}