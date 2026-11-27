// Læser en stregkode (EAN-13, EAN-8, UPC-A, UPC-E, Code 128) fra et billede (ImageData).
// Bruges kun, hvor browseren ikke selv har BarcodeDetector (fx iPhone og Firefox). Bygget af @zxing/library (Apache-2.0) med tools/byg-scanner.sh.
import MultiFormatUPCEANReader from '@zxing/library/esm/core/oned/MultiFormatUPCEANReader.js';
import Code128Reader from '@zxing/library/esm/core/oned/Code128Reader.js';
import BinaryBitmap from '@zxing/library/esm/core/BinaryBitmap.js';
import HybridBinarizer from '@zxing/library/esm/core/common/HybridBinarizer.js';
import RGBLuminanceSource from '@zxing/library/esm/core/RGBLuminanceSource.js';
import DecodeHintType from '@zxing/library/esm/core/DecodeHintType.js';
import BarcodeFormat from '@zxing/library/esm/core/BarcodeFormat.js';
const hints=new Map();hints.set(DecodeHintType.POSSIBLE_FORMATS,[BarcodeFormat.EAN_13,BarcodeFormat.EAN_8,BarcodeFormat.UPC_A,BarcodeFormat.UPC_E]);hints.set(DecodeHintType.TRY_HARDER,true);
const R=[new MultiFormatUPCEANReader(hints),new Code128Reader()];
window.olScan=function(img){const w=img.width,h=img.height,d=img.data,l=new Uint8ClampedArray(w*h);for(let i=0;i<w*h;i++)l[i]=(d[i*4]*77+d[i*4+1]*150+d[i*4+2]*29)>>8;
  const bm=new BinaryBitmap(new HybridBinarizer(new RGBLuminanceSource(l,w,h)));
  for(const r of R){try{return r.decode(bm,hints).getText()}catch(e){}finally{r.reset()}}return null};
