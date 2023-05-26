import matplotlib.pyplot as plt
spectrum = open("spectrum.txt", 'r', encoding='utf-8').readlines()
x = []
y = []
for line in spectrum:
    line = line.strip()
    x.append(float(line.split(", ")[0]))
    y.append(float(line.split(", ")[1]))


