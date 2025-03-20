/************************************
Course: cse 251
File: main.java
Week: week 11 - team activity 1

Instructions:

- Main contains an array of 1,000 random values.  You will be creating
  threads to process this array.  If you find a prime number, display
  it to the console.

- DON'T copy/slice the array in main() for each thread.

Part 1:
- Create a class that is a sub-class of Thread.
- create 4 threads based on this class you created.
- Divide the array among the threads.

Part 2:
- Create a class on an interface or Runnable
- create 4 threads based on this class you created.
- Divide the array among the threads.

Part 3:
- Modify part1 or part 2 to handle any size array and any number
  of threads.

************************************/
import java.util.Random; 
import java.lang.Math; 

class Main {

  static boolean isPrime(long n) 
  { 
      // Corner cases 
      if (n <= 1) return false; 
      if (n <= 3) return true; 
    
      // This is checked so that we can skip  
      // middle five numbers in below loop 
      if (n % 2 == 0 || n % 3 == 0) return false; 
    
      for (long i = 5; i * i <= n; i = i + 6) 
        if (n % i == 0 || n % (i + 2) == 0) 
          return false; 
    
      return true; 
  }

  // Part 1: Sub-class of Thread
  static class PrimeThread extends Thread {
    private long[] array;
    private int start, end;

    PrimeThread(long[] array, int start, int end) {
      this.array = array;
      this.start = start;
      this.end = end;
    }

    @Override
    public void run() {
      for (int i = start; i < end; i++) {
        if (isPrime(array[i])) {
          System.out.println(array[i]);
        }
      }
    }
  }

  // Part 2: Class implementing Runnable
  static class PrimeRunnable implements Runnable {
    private long[] array;
    private int start, end;

    PrimeRunnable(long[] array, int start, int end) {
      this.array = array;
      this.start = start;
      this.end = end;
    }

    @Override
    public void run() {
      for (int i = start; i < end; i++) {
        if (isPrime(array[i])) {
          System.out.println(array[i]);
        }
      }
    }
  }

  public static void main(String[] args) {
    System.out.println("Hello world!");

    // create instance of Random class 
    Random rand = new Random(); 

    int count = 1000;
    long[] array = new long[count];
    for (int i = 0; i < count; i++) 
    {
      array[i] = Math.abs(rand.nextInt());
    }

    // Part 1: Using PrimeThread
    int numThreads = 4;
    int chunkSize = count / numThreads;
    Thread[] threads = new Thread[numThreads];
    for (int i = 0; i < numThreads; i++) {
      int start = i * chunkSize;
      int end = (i == numThreads - 1) ? count : start + chunkSize;
      threads[i] = new PrimeThread(array, start, end);
      threads[i].start();
    }
    for (Thread t : threads) {
      try {
        t.join();
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }

    // Part 2: Using PrimeRunnable
    Thread[] runnableThreads = new Thread[numThreads];
    for (int i = 0; i < numThreads; i++) {
      int start = i * chunkSize;
      int end = (i == numThreads - 1) ? count : start + chunkSize;
      runnableThreads[i] = new Thread(new PrimeRunnable(array, start, end));
      runnableThreads[i].start();
    }
    for (Thread t : runnableThreads) {
      try {
        t.join();
      } catch (InterruptedException e) {
        e.printStackTrace();
      }
    }
  }
}