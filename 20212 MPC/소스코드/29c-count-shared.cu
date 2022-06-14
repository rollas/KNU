#include "./common.cpp"

// input parameters
const unsigned BLOCK_SIZE = 1024;
unsigned NUM = 64 * 1024 * 1024; // num of samplings

// CUDA device variables
__device__ unsigned long long dev_count = 0;

// CUDA kernel function
__global__ void kernelCount( unsigned num ) {
	__shared__ unsigned long long s_count;
	register unsigned i = threadIdx.x + blockIdx.x * blockDim.x;
	if (threadIdx.x == 0) {
		s_count = 0;
	}
	__syncthreads();
	if (i < num) {
		atomicAdd( &s_count, 1ULL );
	}
	__syncthreads();
	if (threadIdx.x == 0) {
		atomicAdd( &dev_count, s_count );
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
	printf("NUM = %d\n", NUM);
	// CUDA kernel launch
	dim3 dimBlock( BLOCK_SIZE, 1, 1 );
	dim3 dimGrid( div_up(NUM, dimBlock.x), 1, 1 );
	ELAPSED_TIME_BEGIN(0);
	kernelCount <<< dimGrid, dimBlock>>>( NUM );
	cudaDeviceSynchronize();
	ELAPSED_TIME_END(0);
	CUDA_CHECK_ERROR();
	// copy to host from device
	unsigned long long count;
	cudaMemcpyFromSymbol( &count, dev_count, sizeof(unsigned long long), 0, cudaMemcpyDeviceToHost );
	CUDA_CHECK_ERROR();
	// check the result
	printf("num thread launched = %d\n", NUM);
	printf("count = %llu\n", count);
	// done
	return 0;
}
