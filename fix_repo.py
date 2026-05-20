with open('services/validator/app/repositories/schema_repo.py', 'r') as f:
    content = f.read()

content = content.replace("await self.session.add(", "self.session.add(")

with open('services/validator/app/repositories/schema_repo.py', 'w') as f:
    f.write(content)
