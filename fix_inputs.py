def fix_css(filepath):
    with open(filepath, "r") as f:
        html = f.read()

    # For admin.html
    html = html.replace('''        input[type="text"], input[type="number"], textarea { 
            width: 100%; 
            padding: 1rem 1.2rem; 
            background: rgba(255,255,255,0.03); 
            border: 1px solid rgba(255,255,255,0.08); 
            color: var(--light); 
            border-radius: 8px; 
            font-family: inherit;
            font-size: 1rem;
            transition: all 0.3s; 
        }''', '''        input[type="text"], input[type="number"], textarea { 
            width: 100%; 
            padding: 1rem 0; 
            background: transparent; 
            border: none;
            border-bottom: 2px solid rgba(255,255,255,0.2); 
            color: var(--light); 
            border-radius: 0; 
            font-family: inherit;
            font-size: 1rem;
            transition: all 0.3s; 
        }''')

    html = html.replace('''        .modal-content input[type="text"], 
        .modal-content input[type="number"], 
        .modal-content textarea {
            background-color: rgba(255,255,255,0.03);
            border: none;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            border-radius: 4px 4px 0 0;
            color: var(--light);
            padding: 1rem;
            transition: all 0.3s;
        }''', '''        .modal-content input[type="text"], 
        .modal-content input[type="number"], 
        .modal-content textarea {
            background-color: transparent;
            border: none;
            border-bottom: 2px solid rgba(255,255,255,0.2);
            border-radius: 0;
            color: var(--light);
            padding: 1rem 0;
            transition: all 0.3s;
        }''')

    html = html.replace('body.light-mode input[type="text"], body.light-mode input[type="number"], body.light-mode textarea { background: #fff; border: 1px solid #E8DDD0; color: #1C1008; }',
                        'body.light-mode input[type="text"], body.light-mode input[type="number"], body.light-mode textarea { background: transparent !important; border: none !important; border-bottom: 2px solid #D4C4B0 !important; color: #1C1008 !important; border-radius: 0 !important; }')

    # For login.html
    html = html.replace('''        .auth-input-group input { width: 100%; padding: 1rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: var(--light); border-radius: 10px; font-family: 'Playfair Display', serif; font-size: 1rem; outline: none; transition: border 0.3s; }''',
                        '''        .auth-input-group input { width: 100%; padding: 1rem 0; background: transparent; border: none; border-bottom: 2px solid rgba(255,255,255,0.2); color: var(--light); border-radius: 0; font-family: 'Playfair Display', serif; font-size: 1rem; outline: none; transition: border 0.3s; }''')

    html = html.replace('input:focus, textarea:focus { outline: none; border-color: var(--primary); background: rgba(255,255,255,0.06); box-shadow: 0 0 0 4px rgba(203, 168, 124, 0.1); }',
                        'input:focus, textarea:focus { outline: none; border-bottom-color: var(--primary) !important; background: transparent !important; box-shadow: none !important; }')
    
    html = html.replace('.modal-content input:focus, \n        .modal-content textarea:focus {\n            border-bottom: 2px solid var(--primary);\n            outline: none;\n            background-color: rgba(255,255,255,0.06);\n        }',
                        '.modal-content input:focus, \n        .modal-content textarea:focus {\n            border-bottom: 2px solid var(--primary);\n            outline: none;\n            background-color: transparent;\n        }')

    html = html.replace('.auth-input-group input:focus { border-color: var(--primary); }',
                        '.auth-input-group input:focus { border-bottom-color: var(--primary); }')
    

    with open(filepath, "w") as f:
        f.write(html)

fix_css("app/templates/admin.html")
fix_css("app/templates/login.html")
print("Fixed inputs")
