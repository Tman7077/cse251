/*
	---------------------------------------

Course: CSE 251
Lesson Week: ?12
File: team.go
Author: Brother Comeau

Purpose: team activity - finding primes

Instructions:

- Process the array of numbers, find the prime numbers using goroutines

worker()

This goroutine will take in a list/array/channel of numbers.  It will place
prime numbers on another channel

readValue()

This goroutine will display the contents of the channel containing
the prime numbers

---------------------------------------
*/
package main

import (
	"fmt"
	"math/rand"
	"time"
)

func isPrime(n int) bool {
	// Primality test using 6k+-1 optimization.
	// From: https://en.wikipedia.org/wiki/Primality_test

	if n <= 3 {
		return n > 1
	}

	if n%2 == 0 || n%3 == 0 {
		return false
	}

	i := 5
	for (i * i) <= n {
		if n%i == 0 || n%(i+2) == 0 {
			return false
		}
		i += 6
	}
	return true
}

func worker(numbers <-chan int, primes chan<- int, done chan<- bool) {
	// TODO - process numbers on one channel and place prime number on another
	for num := range numbers {
		if isPrime(num) {
			primes <- num
		}
	}
	done <- true
}

func readValues(primes <-chan int) {
	// TODO -Display prime numbers from a channel
	for prime := range primes {
		fmt.Println(prime)
	}
}

func main() {

	workers := 10
	numberValues := 100

	// Create any channels that you need
	// Create any other "things" that you need to get the workers to finish(join)

	numbers := make(chan int, numberValues)
	primes := make(chan int, numberValues)
	done := make(chan bool, workers)

	// create workers
	for w := 1; w <= workers; w++ {
		go worker(numbers, primes, done) // Add any arguments
	}

	rand.Seed(time.Now().UnixNano())
	for i := 0; i < numberValues; i++ {
		// ch <- rand.Int()
		numbers <- rand.Int()
	}
	close(numbers)

	go readValues(primes) // Add any arguments

	for w := 1; w <= workers; w++ {
		<-done
	}
	close(primes)

	fmt.Println("All Done!")
}
