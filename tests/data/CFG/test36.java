public class Test {
    void loadSubdivisions() {
      InputStream iso3166_2Resource = this.getClass().getResourceAsStream(ISO_3166_2_LOCATION);
      if (iso3166_2Resource == null) {
        throw new IllegalStateException(
          "Can't find the list of subdivisions! Expected location was:" +
          ISO_3166_2_LOCATION
        );
      }
      XmlConverter<ISO3166_2_CountryEntity> converter = new XmlConverter<>(
        "iso_3166_country",
        ISO3166_2_CountryEntity.class
      );
      ObservableList<ISO3166_2_CountryEntity> subdivisionsEntities = FXCollections.observableArrayList();
      try {
        DataReader<ISO3166_2_CountryEntity> dataSource = new InputStreamSource<>(
          iso3166_2Resource,
          converter
        );
        ListDataProvider<ISO3166_2_CountryEntity> listDataProvider = new ListDataProvider<>(
          dataSource
        );
        listDataProvider.setResultObservableList(subdivisionsEntities);
        Worker<ObservableList<ISO3166_2_CountryEntity>> worker = listDataProvider.retrieve();
        worker.stateProperty().addListener(obs -> {
            if (worker.getState() == Worker.State.SUCCEEDED) {
              subdivisionsEntities.forEach(entity -> {
                if (entity.subsets != null && !entity.subsets.isEmpty()) {
                  Country country = findCountryByCode(entity.code);
                  if (!countryCodeSubdivisionMap.containsKey(country)) {
                    countryCodeSubdivisionMap.put(country, new ArrayList<>());
                  }
                  List<Subdivision> subdivisionList = countryCodeSubdivisionMap.get(
                    country
                  );
                     entity.subsets.forEach(subset -> {
                             subset.entryList.forEach(entry -> {
                                     subdivisionList.add(new Subdivision(entry.name, entry.code, country));
                             });
                     });
  
                     String subdivisionName = entity.subsets.stream()
                                     .map(subset -> subset.subdivisionType)
                                     .collect(Collectors.joining("/"));
  
                  countryCodeSubdivisionNameMap.put(country, subdivisionName);
                }
              });
              inProgress.set(false);
            }
          });
      } catch (IOException e) {
        LOG.error("A problem was detected while loading the XML file with the available subdivisions.", e);
      }
    }
  }