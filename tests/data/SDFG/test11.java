public class Function {
public boolean isInNet(String host, String pattern, String mask) {
    host = dnsResolve(host);
    if (host == null || host.length() == 0) {
      return false;
    }
    long lhost = parseIpAddressToLong(host);
    long lpattern = parseIpAddressToLong(pattern);
    long lmask = parseIpAddressToLong(mask);
    return (lhost & lmask) == lpattern;
}
}