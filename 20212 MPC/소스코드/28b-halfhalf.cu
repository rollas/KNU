#include "./common.cpp"

// input parameters
const unsigned BLOCK_SIZE = 1024;
unsigned NUM = 256 * 1024 * 1024; // num of samplings

// CUDA kernel function
__global__ void kernelHalfHalf( float* dst, const float* src, unsigned num, unsigned half ) {
	register unsigned i = blockIdx.x * blockDim.x + threadIdx.x;
	if (i < num) {
		if (i < half) { // left half
			dst[i] = src[i * 2];
		} else {
			dst[i] = src[(i - half) * 2 + 1];
		}
	}
}

int main( const int argc, const char* argv[] ) {
	// argv processing
	switch (argc) {
	case 1:
		break;
	case 2:
		NUM = procArg( argv[0], argv[1], 1 );
		break;
	default:
		printf("usage: %s [num]\n", argv[0]);
		exit(EXIT_FAILURE); // EINVAL: invalid argument
		break;
	}
	if (NUM % 2 != 0) {
		printf("%s: ERROR: invalid num = %d\n", argv[0], NUM);
		exit(EXIT_FAILURE); // EINVAL: invalid argument
	}
	printf("num=%d\n", NUM);
	// host-side data
	float* src = new float[NUM];
	float* dst = new float[NUM];
	// set random data
	srand( 0 );
	setNormalizedRandomData( src, NUM );
	// device-side data
	float* dev_src = nullptr;
	float* dev_dst = nullptr;
	// allocate device memory
	cudaMalloc( (void**)&dev_src, NUM * sizeof(float) );
	cudaMalloc( (void**)&dev_dst, NUM * sizeof(float) );
	CUDA_CHECK_ERROR();
	// copy to device from host
	ELAPSED_TIME_BEGIN(1);
	cudaMemcpy( dev_src, src, NUM * sizeof(float), cudaMemcpyHostToDevice );
	CUDA_CHECK_ERROR();
	// CUDA kernel launch
	dim3 dimBlock( BLOCK_SIZE, 1, 1 );
	dim3 dimGrid( div_up(NUM, dimBlock.x), 1, 1 );
	CUDA_PRINT_CONFIG( NUM );
	ELAPSED_TIME_BEGIN(0);
	kernelHalfHalf <<< dimGrid, dimBlock>>>( dev_dst, dev_src, NUM, NUM / 2 );
	cudaDeviceSynchronize();
	ELAPSED_TIME_END(0);
	CUDA_CHECK_ERROR();
	// copy to host from device
	cudaMemcpy( dst, dev_dst, NUM * sizeof(float), cudaMemcpyDeviceToHost );
	ELAPSED_TIME_END(1);
	CUDA_CHECK_ERROR();
	// free device memory
	cudaFree( dev_src );
	cudaFree( dev_dst );
	CUDA_CHECK_ERROR();
	// check the result
	float sumDst = getSum( dst, NUM );
	float sumSrc = getSum( src, NUM );
	float diff = fabsf( sumDst - sumSrc );
	printf("sumDst = %f\n", sumDst);
	printf("sumSrc = %f\n", sumSrc);
	printf("diff(sumDst, sumSrc) = %f\n", diff);
	printVec( "dst", dst, NUM );
	printVec( "src", src, NUM );
	// cleaning
	delete[] src;
	delete[] dst;
	// done
	return 0;
}
