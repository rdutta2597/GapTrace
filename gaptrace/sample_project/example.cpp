#include <iostream>
#include <string>

// Function with decision points
int validateAge(int age) {
    if (age < 0) {
        return -1;  // Critical error path
    }
    
    if (age < 18) {
        return 0;
    } else {
        return 1;
    }
}

// Function with switch and loop
std::string getStatus(int code) {
    switch (code) {
        case 200:
            return "OK";
        case 404:
            return "Not Found";
        case 500:
            return "Server Error";
        default:
            return "Unknown";
    }
}

// Function with null check (critical)
int processData(int* ptr, int size) {
    if (ptr == nullptr) {  // Critical null check
        return -1;
    }
    
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += ptr[i];
    }
    
    return sum;
}

// Complex branching
double calculateDiscount(double amount, bool isPremium, int yearsCustomer) {
    double discount = 0.0;
    
    if (isPremium) {
        discount = 0.2;  // 20% discount for premium
    } else if (yearsCustomer > 5) {
        discount = 0.1;  // 10% for loyal customers
    } else if (amount > 1000) {
        discount = 0.05; // 5% for large orders
    }
    
    return amount * (1.0 - discount);
}
