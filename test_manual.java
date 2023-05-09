public class test {
public boolean equals ( Object obj ) {
if ( ! ( obj instanceof FacetLabel ) ) {
return false ; }
FacetLabel other = ( FacetLabel ) obj ;
if ( length != other . length ) {
return false ; }
for (
int i = length - 1 ; i >= 0 ; i -- ) {
if ( ! components [ i ] . equals ( other . components [ i ] ) ) {
return false ; } }
return true ; } }