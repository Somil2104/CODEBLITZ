from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from login_utils import login_required 
import re 
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    solutions = db.relationship('Solution', backref='user', lazy=True)

# Challenge model
class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    test_cases = db.Column(db.JSON, nullable=True)  # Made nullable for backwards compatibility
    initial_code = db.Column(db.Text, nullable=True) # Made nullable for backwards compatibility
    function_name = db.Column(db.String(100), nullable=True) # Made nullable for backwards compatibility
    # Add relationship to solutions
    solutions = db.relationship('Solution', backref='challenge', lazy=True)

# Add new model for tracking solutions
class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    passed = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

def add_sample_challenges():
    if Challenge.query.first() is not None:
        return

    sample_challenges = [
        {
            'title': 'FizzBuzz',
            'description': 'Write a function fizzbuzz(n) that returns a list of numbers from 1 to n where multiples of three are replaced with "Fizz", multiples of five with "Buzz", and multiples of both with "FizzBuzz".',
            'difficulty': 'Easy',
            'test_cases': [
                {'input': '15', 'expected': ['1','2','Fizz','4','Buzz','Fizz','7','8','Fizz','Buzz','11','Fizz','13','14','FizzBuzz']},
                {'input': '5', 'expected': ['1','2','Fizz','4','Buzz']}
            ],
            'initial_code': 'def fizzbuzz(n):\n    result = []\n    # Write your code here\n    return result',
            'function_name': 'fizzbuzz'
        },
        {
            'title': 'Two Sum',
            'description': 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target.',
            'difficulty': 'Medium',
            'test_cases': [
                {'input': '[2,7,11,15], 9', 'expected': [0,1]},
                {'input': '[3,2,4], 6', 'expected': [1,2]}
            ],
            'initial_code': 'def two_sum(nums, target):\n    # Write your code here\n    return []',
            'function_name': 'two_sum'
        },
        {
            'title': 'Palindrome Number',
            'description': 'Write a function that returns True if the given number is a palindrome (reads the same backward as forward).',
            'difficulty': 'Easy',
            'test_cases': [
                {'input': '121', 'expected': True},
                {'input': '-121', 'expected': False}
            ],
            'initial_code': 'def is_palindrome(x):\n    # Write your code here\n    return False',
            'function_name': 'is_palindrome'
        },
        {
            'title': 'Valid Parentheses',
            'description': 'Given a string containing just the characters "(", ")", "{", "}", "[" and "]", determine if the input string is valid.',
            'difficulty': 'Medium',
            'test_cases': [
                {'input': '()', 'expected': True},
                {'input': '([)]', 'expected': False}
            ],
            'initial_code': 'def is_valid(s):\n    # Write your code here\n    return False',
            'function_name': 'is_valid'
        },
        {
            'title': 'Maximum Subarray',
            'description': 'Find the contiguous subarray with the largest sum and return its sum.',
            'difficulty': 'Medium',
            'test_cases': [
                {'input': '[-2,1,-3,4,-1,2,1,-5,4]', 'expected': 6},
                {'input': '[1]', 'expected': 1}
            ],
            'initial_code': 'def max_subarray(nums):\n    # Write your code here\n    return 0',
            'function_name': 'max_subarray'
        },
        {
            'title': 'First Missing Positive',
            'description': 'Given an unsorted integer array nums, return the smallest missing positive integer.',
            'difficulty': 'Hard',
            'test_cases': [
                {'input': '[1,2,0]', 'expected': 3},
                {'input': '[3,4,-1,1]', 'expected': 2}
            ],
            'initial_code': 'def first_missing_positive(nums):\n    # Write your code here\n    return 0',
            'function_name': 'first_missing_positive'
        },
        {
            'title': 'Merge Intervals',
            'description': 'Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals.',
            'difficulty': 'Medium',
            'test_cases': [
                {'input': '[[1,3],[2,6],[8,10],[15,18]]', 'expected': [[1,6],[8,10],[15,18]]},
                {'input': '[[1,4],[4,5]]', 'expected': [[1,5]]}
            ],
            'initial_code': 'def merge(intervals):\n    # Write your code here\n    return []',
            'function_name': 'merge'
        },
        {
            'title': 'Regular Expression Matching',
            'description': 'Implement regular expression matching with support for "." and "*".',
            'difficulty': 'Hard',
            'test_cases': [
                {'input': '"aa", "a*"', 'expected': True},
                {'input': '"ab", ".*"', 'expected': True}
            ],
            'initial_code': 'def is_match(s, p):\n    # Write your code here\n    return False',
            'function_name': 'is_match'
        },
        {
            'title': 'Climbing Stairs',
            'description': 'You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?',
            'difficulty': 'Easy',
            'test_cases': [
                {'input': '2', 'expected': 2},
                {'input': '3', 'expected': 3}
            ],
            'initial_code': 'def climb_stairs(n):\n    # Write your code here\n    return 0',
            'function_name': 'climb_stairs'
        }
    ]

    for challenge_data in sample_challenges:
        challenge = Challenge(**challenge_data)
        db.session.add(challenge)
    
    db.session.commit()

@app.context_processor
def utility_processor():
    def get_dark_mode():
        return session.get('dark_mode', False)
    return dict(get_dark_mode=get_dark_mode)

@app.route('/toggle-theme', methods=['POST'])
def toggle_theme():
    session['dark_mode'] = not session.get('dark_mode', False)
    return {'success': True}

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate username uniqueness
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please choose another.', 'danger')
            return redirect("/")

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email address! Please enter a valid email.', 'danger')
            return redirect("/")

        # Check if email is unique
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('An account with this email already exists!', 'danger')
            return redirect("/")
        
        # Hash password and save user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect("/")

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect("/")
    return render_template("register.html")
    
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect("/")

@app.route('/profile')
@login_required
def profile():
    user = db.session.get(User, session['user_id'])  # Updated to use session.get
    stats = {
        'total_solved': Solution.query.filter_by(user_id=user.id, passed=True).count(),
        'total_attempts': Solution.query.filter_by(user_id=user.id).count(),
        'challenges_by_difficulty': {
            'Easy': 0,
            'Medium': 0,
            'Hard': 0
        }
    }
    
    # Get solved challenges by difficulty
    solved_challenges = (
        db.session.query(Challenge.difficulty, db.func.count(Challenge.id))
        .join(Solution)
        .filter(Solution.user_id == user.id, Solution.passed == True)
        .group_by(Challenge.difficulty)
        .all()
    )
    
    for difficulty, count in solved_challenges:
        stats['challenges_by_difficulty'][difficulty] = count

    # Get recent solutions with challenge information
    recent_solutions = (
        Solution.query
        .filter_by(user_id=user.id)
        .order_by(Solution.submitted_at.desc())
        .limit(5)
        .all()
    )
    
    return render_template('profile.html', user=user, stats=stats, recent_solutions=recent_solutions)

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')  # Get the logged-in user's username
    return render_template('dashboard.html', username=username)

@app.route('/challenges')
def challenges():
    challenges = Challenge.query.all()
    return render_template('challenges.html', challenges=challenges)

@app.route('/challenge/<int:challenge_id>')
def challenge_detail(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    return render_template('challenge_detail.html', challenge=challenge)

@app.route('/submit_solution/<int:challenge_id>', methods=['POST'])
def submit_solution(challenge_id):
    if not session.get('user_id'):
        return jsonify({
            'success': False,
            'error': 'Please login to submit solutions'
        }), 401

    try:
        data = request.get_json()
        if not data or 'solution' not in data:
            return jsonify({
                'success': False,
                'error': 'No solution provided'
            }), 400

        solution = data['solution']
        challenge = Challenge.query.get_or_404(challenge_id)
        
        # Create a safe execution environment
        local_dict = {}
        # Add any required built-in functions to the globals
        allowed_globals = {
            'print': print,
            'len': len,
            'range': range,
            'list': list,
            'str': str,
            'int': int,
            'sorted': sorted,  # Add more built-in functions
            'set': set,
            'dict': dict,
            'max': max,
            'min': min,
            'sum': sum,
            'abs': abs,
        }
        
        try:
            # Execute the user's solution
            exec(solution, allowed_globals, local_dict)
            
            # Get the function from the solution
            user_function = local_dict.get(challenge.function_name)
            if not user_function:
                return jsonify({
                    'success': False,
                    'error': f"Function '{challenge.function_name}' not found in your solution. Make sure you've defined it correctly."
                }), 400
            
            # Test the solution
            results = []
            all_tests_passed = True
            
            for test_case in challenge.test_cases:
                try:
                    # Handle different input types
                    input_data = test_case['input']
                    if ',' in input_data and not input_data.startswith('['):
                        # Handle multiple arguments
                        args = [eval(arg.strip()) for arg in input_data.split(',')]
                        result = user_function(*args)
                    elif input_data.startswith('['):
                        # Handle array/matrix input
                        args = eval(input_data)
                        if isinstance(args, tuple):
                            result = user_function(*args)
                        else:
                            result = user_function(args)
                    else:
                        # Handle simple input
                        result = user_function(eval(input_data))
                    
                    # Compare results
                    passed = result == test_case['expected']
                    results.append({
                        'input': test_case['input'],
                        'expected': test_case['expected'],
                        'actual': result,
                        'passed': passed
                    })
                    if not passed:
                        all_tests_passed = False
                        
                except Exception as e:
                    results.append({
                        'input': test_case['input'],
                        'error': str(e),
                        'passed': False
                    })
                    all_tests_passed = False
            
            # Save the solution attempt
            solution = Solution(
                user_id=session['user_id'],
                challenge_id=challenge_id,
                code=data['solution'],
                passed=all_tests_passed
            )
            db.session.add(solution)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'all_tests_passed': all_tests_passed,
                'results': results
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f"Error executing your code: {str(e)}"
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}"
        }), 500

with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    add_sample_challenges()

if __name__ == '__main__':
    app.run(debug=True)