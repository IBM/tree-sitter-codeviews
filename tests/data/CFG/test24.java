public class Test {

    public IndexableField getField(FieldInfo fieldInfo) {
      fieldNames.add(fieldInfo.name);
      List<LazyField> values = fields.get(fieldInfo.number);
      if (null == values) {
        values = new ArrayList<>();
        fields.put(fieldInfo.number, values);
      }
      LazyField value = new LazyField(fieldInfo.name, fieldInfo.number);
      values.add(value);
      synchronized (this) {
        doc = null;
      }
      return value;
    }
  }