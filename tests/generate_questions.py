import json
import random
import os

domains = [
    ('Physics', ['What is the theory of relativity?', 'Explain quantum entanglement.', 'What are black holes?', 'Define the speed of light.', 'Who discovered gravity?']),
    ('Geography', ['What is the capital of France?', 'Where is Amrita Vishwa Vidyapeetham located?', 'What is the tallest mountain?', 'Name the oceans.', 'Where is the Amazon river?']),
    ('Coding', ['Write a python script to calculate the 15th Fibonacci number.', 'Explain polymorphism in OOP.', 'What is a closure in JavaScript?', 'How do you reverse a string in Python?', 'Write a C++ program to find the factorial of 5.']),
    ('History', ['Who won World War 2?', 'When was the Declaration of Independence signed?', 'Who was the first emperor of China?', 'Explain the Renaissance.', 'What was the Cold War?']),
    ('Math', ['What is the derivative of x squared?', 'Explain Pythagorean theorem.', 'What is the square root of 144?', 'Calculate 15 * 32.', 'What is Eulers number?']),
    ('Technology', ['Who created JavaScript?', 'What is the purpose of Docker?', 'Explain blockchain.', 'What is an API?', 'Who founded Microsoft?']),
    ('Biology', ['What is DNA?', 'Explain photosynthesis.', 'What is the powerhouse of the cell?', 'How do vaccines work?', 'What is mitosis?']),
    ('Literature', ['Who wrote Romeo and Juliet?', 'What is 1984 about?', 'Who is the author of Harry Potter?', 'Explain the plot of To Kill a Mockingbird.', 'What is a haiku?']),
    ('Space', ['How far is the moon?', 'What is the Hubble Space Telescope?', 'Is there water on Mars?', 'What is a supernova?', 'Who was the first person in space?']),
    ('Logic', ['If all bloops are razzies and all razzies are lazzies, are all bloops lazzies?', 'What comes next: 2, 4, 8, 16, ?', 'Solve: 5 + 2 * 3', 'Are tomatoes a fruit or vegetable?', 'What is the Monty Hall problem?'])
]

questions = []
for _ in range(10):
    for domain, q_list in domains:
        questions.append(random.choice(q_list))

os.makedirs('tests', exist_ok=True)
with open('tests/eval_questions.json', 'w') as f:
    json.dump(questions, f, indent=4)
print('100 questions generated.')
