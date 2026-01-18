from collections import defaultdict

words = ["apple", "banana", "apple", "orange", "banana", "banana"]

d = defaultdict(int)

# for i in words:
#     d[i] = d.get(i) + 1
# print(d)

print(d['a'])