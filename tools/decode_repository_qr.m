#import <Foundation/Foundation.h>
#import <Vision/Vision.h>
int main(int argc, const char **argv) { @autoreleasepool {
 VNDetectBarcodesRequest *req=[VNDetectBarcodesRequest new];req.usesCPUOnly=YES;req.symbologies=@[VNBarcodeSymbologyQR];
 VNImageRequestHandler *h=[[VNImageRequestHandler alloc] initWithURL:[NSURL fileURLWithPath:[NSString stringWithUTF8String:argv[1]]] options:@{}];NSError *e=nil;
 if (![h performRequests:@[req] error:&e]) {NSLog(@"%@",e);return 1;}
 for(VNBarcodeObservation *v in req.results) printf("%s\n",[v.payloadStringValue UTF8String]);return req.results.count?0:2;
}}
