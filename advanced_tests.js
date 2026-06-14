// 1. Array callback methods and arrow functions
let nums = [1, 2, 3, 4, 5];
let doubled = nums.map(x => x * 2);
console.log("Doubled:", doubled.join(", "));

let evens = nums.filter(x => x % 2 === 0);
console.log("Evens:", evens.join(", "));

let sum = nums.reduce((acc, curr) => acc + curr, 0);
console.log("Sum:", sum);

let found = nums.find(x => x > 3);
console.log("Found > 3:", found);

let hasOdd = nums.some(x => x % 2 !== 0);
console.log("Has odd:", hasOdd);

let allPositive = nums.every(x => x > 0);
console.log("All positive:", allPositive);

// 2. Date handling
let date = new Date(2026, 5, 13, 15, 30); // June 13, 2026 15:30 (Month is 0-indexed in JS)
console.log("Date full year:", date.getFullYear());
console.log("Date month:", date.getMonth()); // should be 5
console.log("Date day:", date.getDate()); // should be 13
console.log("Date hours:", date.getHours()); // should be 15
console.log("Date minutes:", date.getMinutes()); // should be 30

// 3. Rest parameter and Spread operator
function average(...args) {
    let s = args.reduce((a, b) => a + b, 0);
    return s / args.length;
}
console.log("Average:", average(10, 20, 30, 40));

let extraNums = [6, 7];
let merged = [...nums, ...extraNums];
console.log("Merged:", merged.join(", "));

// 4. Object dynamic property access
let obj = {};
obj.name = "Viswa";
obj["age"] = 22;
console.log("Object:", obj.name, "age " + obj.age);

// 5. do...while loop
let count = 0;
do {
    count++;
} while (count < 3);
console.log("do...while count:", count);

// 6. Logical operators short-circuit
console.log("OR short-circuit:", null || "default");
console.log("AND short-circuit:", "value" && 123);

// 7. Math functions
console.log("Math.abs:", Math.abs(-10));
console.log("Math.ceil:", Math.ceil(4.2));
console.log("Math.max:", Math.max(1, 5, 3));
console.log("Math.min:", Math.min(1, 5, 3));

// 8. Switch statement with fallthrough
let option = 2;
switch (option) {
    case 1:
        console.log("Case 1");
        break;
    case 2:
        console.log("Case 2");
    case 3:
        console.log("Case 2 or 3 (fallthrough)");
        break;
    default:
        console.log("Default");
}
