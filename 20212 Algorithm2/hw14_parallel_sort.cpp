/*
16
387 120 190 124 376 339 452 425 126 11 289 327 353 451 295 119
204 487 377 332 45 432 225 153 420 85 318 276 143 315 323 327
394 113 373 63 221 425 93 425 329 389 457 141 204 359 7 459
90 461 170 66 388 154 381 445 134 134 333 156 174 63 198 239
288 473 284 22 455 295 156 375 430 192 197 0 146 42 478 382
48 130 43 467 29 316 421 185 405 130 98 435 467 56 365 313
268 175 271 449 413 215 1 371 143 252 185 448 412 465 88 315
481 258 282 49 184 449 225 109 298 237 80 283 187 361 378 168
240 371 59 135 389 381 124 190 91 175 381 481 399 109 456 278
104 380 52 385 324 207 407 149 491 100 434 215 261 79 21 424
327 178 162 425 32 305 458 13 4 336 233 134 467 387 35 390
340 303 416 183 84 263 216 436 471 228 197 393 276 230 15 500
450 291 173 5 264 321 69 124 131 385 367 97 324 326 216 363
17 405 0 407 359 14 336 91 136 9 288 131 379 352 217 4
250 478 473 7 249 394 258 190 218 443 99 2 349 477 213 307
181 239 438 164 193 383 181 143 492 498 217 80 268 207 308 350
*/

#include <iostream>
#include <iomanip>
#include <fstream>
#include <limits.h>
#include <math.h>
#include <algorithm>

using namespace std;

#define isEven(x) (x%2==0)? true : false
#define isOdd(x) (x%2==1)? true : false

void swapint(int* a, int* b, int* temp)
{
	*temp = *a;
	*a = *b;
	*b = *temp;
}
bool cmp_ltoh(int a, int b)
{
 	return a < b;
}
bool cmp_htol(int a, int b)
{
	return a > b;
}
void sort_x_axis(int** M, int y, int n)
{
	for (int i = 1; i <= n; ++i)
	{
		for (int j = 1; j < n; ++j)
		{
			int* a = M[j - 1] + y;
			int* b = M[j] + y;
			int temp;
			if (*b < *a)
				swapint(a, b, &temp);
		}
	}
}
void sort_y_axis_ltoh(int** M, int x, int n)
{
	sort(M[x], M[x] + n, cmp_ltoh);
}
void sort_y_axis_htol(int** M, int x, int n)
{
	sort(M[x], M[x] + n, cmp_htol);
}
void print2Di(const char* txt, int** M, int n, int w)
{
	cout << txt << endl;
	for (int i = 0; i < n; ++i)
	{
		for (int j = 0; j < n; ++j)
			cout << setw(w) << M[i][j];
		cout << endl;
	}
}

void parallel_sort(int** M, int n)
{
	int logn = (int) log2(n);	
	
	for (int i = 0; i < logn; ++i)
	{
		for (int x = 0; x < n; ++x)
		{
			if (isEven(x))
				sort_y_axis_ltoh(M, x, n);
			else
				sort_y_axis_htol(M, x, n);
		}

		for (int y = 0; y < n; ++y)
			sort_x_axis(M, y, n);
	}
	for (int x = 0; x < n; ++x)
		sort_y_axis_ltoh(M, x, n);
}



int main()
{
	ifstream input("input.txt");

	// input: (matrix size)
	int n = 1;
	input >> n;
	
	int** M = new int* [n];
	for (int i = 0; i < n; ++i)
		M[i] = new int[n];

	// input: (nxn matrix)
	for (int i = 0; i < n; ++i)
		for (int j = 0; j < n; ++j)
			input >> M[i][j];

	print2Di("before:", M, n, 5);

	parallel_sort(M, n);

	cout << endl;
	print2Di("after:", M, n, 5);
}