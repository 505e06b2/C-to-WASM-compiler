void test(int *h) {
	*h = 2;
}

int main() {
	int g = 1;
	test(&g);
	return g;
}