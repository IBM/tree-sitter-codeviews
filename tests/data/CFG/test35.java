public class Test {
    public static <B, S extends B> ImmutableClassToInstanceMap<B> copyOf(
         Map<? extends Class<? extends S>, ? extends S> map) {
       if (map instanceof ImmutableClassToInstanceMap) {
         @SuppressWarnings("unchecked") // covariant casts safe (unmodifiable)
         // Eclipse won't compile if we cast to the parameterized type.
         ImmutableClassToInstanceMap<B> cast = (ImmutableClassToInstanceMap) map;
         return cast;
       }
       return new Builder<B>().putAll(map).build();
     }
   }