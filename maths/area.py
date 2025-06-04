#!/bin/bash

width = int(input('width:  '))
height = int(input('height:  '))
px = int(input('place x'))
py = int(input('place y'))

w = width/2
h = height/2

ul = [px -w, py - h]
ur = [px + w, py - h]
bl = [px - w, py + h]
br = [px + w, py + h]

points = [ul, ur, bl, br]

def halfway(point_1, point_2):
    return (point_1 + point_2)/2

x = 0
y = 1

def halfway_on_axis(point_1, point_2, axis = x):
    return halfway(point_1[axis], point_2[axis])

def halfway_between_points(point_1, point_2):
    return[halfway_on_axis(point_1, point_2, x), halfway_on_axis(point_1, point_2, y)]

answer = halfway_between_points(ul, ur)

print(f"halfway between {ul} and {ur} is {answer}")