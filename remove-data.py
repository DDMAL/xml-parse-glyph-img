import os

print('What data should be removed? Training (0), Testing (1), All (2) ')
choice = int(input().strip())

if choice == 0:
    os.system('rm -rf position_train position_train.zip position_train.txt')
elif choice == 1:
    os.system('rm -rf position_test position_test.zip position_test.txt')
elif choice == 2:
    os.system('rm -rf position_test position_train position_test.zip position_train.zip position_test.txt position_train.txt')
