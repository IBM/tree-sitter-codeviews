public class Simple {
    public override void Decompress(DataInput input, int originalLength, int offset, int length, BytesRef bytes){
        Debug.Assert(offset + length <= originalLength);
        if (length == 0){
            bytes.Length = 0;
            return;
        }
        byte[] compressedBytes = new byte[input.ReadVInt32()];
        input.ReadBytes(compressedBytes, 0, compressedBytes.Length);
        byte[] decompressedBytes = null;
        using (MemoryStream decompressedStream = new MemoryStream()){
            using (MemoryStream compressedStream = new MemoryStream(compressedBytes)){
                using (DeflateStream dStream = new DeflateStream(compressedStream, System.IO.Compression.CompressionMode.Decompress)){
                dStream.CopyTo(decompressedStream);
                }
            }
            decompressedBytes = decompressedStream.ToArray();
        }
        if (decompressedBytes.Length != originalLength){
            throw new CorruptIndexException("Length mismatch: " + decompressedBytes.Length + " != " + originalLength + " (resource=" + input + ")");
        }
        bytes.Bytes = decompressedBytes;
        bytes.Offset = offset;
        bytes.Length = length;
    }
}