#!/bin/bash
# togel.sh

# 6 digit random (000000-999999)
six=$(od -An -N4 -tu4 /dev/urandom | awk '{printf "%06d\n", $1 % 1000000}')

# 5 digit random (00000-99999)
five=$(od -An -N4 -tu4 /dev/urandom | awk '{printf "%05d\n", $1 % 100000}')

# 4 digit random (0000-9999)
four=$(od -An -N2 -tu2 /dev/urandom | awk '{printf "%04d\n", $1 % 10000}')

# 3 digit random (000-999)
three=$(od -An -N2 -tu2 /dev/urandom | awk '{printf "%03d\n", $1 % 1000}')

# 2 digit random (00-99)
two=$(od -An -N2 -tu2 /dev/urandom | awk '{printf "%02d\n", $1 % 100}')

echo "🎰 Random Lottery Numbers 🎰"
echo "----------------------------"
echo "6D : $six"
echo "5D : $five"
echo "4D : $four"
echo "3D : $three"
echo "2D : $two"
