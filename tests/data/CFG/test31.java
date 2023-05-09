public class test_random {

    public POIFSFileSystem() {
      this(true);
      _header.setBATCount(1);
      _header.setBATArray(new int[] { 1 });
      BATBlock bb = BATBlock.createEmptyBATBlock(bigBlockSize, false);
      bb.setOurBlockIndex(1);
      _bat_blocks.add(bb);
      setNextBlock(0, POIFSConstants.END_OF_CHAIN);
      setNextBlock(1, POIFSConstants.FAT_SECTOR_BLOCK);
      _property_table.setStartBlock(0);
    }
  }