#!/usr/bin/env python3
"""
Seed data script for Accessify development and testing.

Creates mock organizations, users, verified domains, and sample websites.

Usage:
    python seed_data.py
"""

import secrets
from datetime import datetime, timedelta

from dotenv import load_dotenv
import bcrypt
from db import q

# Load environment variables
load_dotenv()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def generate_verification_token() -> str:
    """Generate a cryptographically random verification token."""
    return secrets.token_urlsafe(32)


def seed_ethics_agreement():
    """Create initial ethics agreement."""
    print("Creating ethics agreement...")
    
    content = """# Accessify Ethics Agreement

**Version:** 1.0  
**Effective Date:** December 13, 2024

## Purpose

This Ethics Agreement governs your use of the Accessify platform ("Service"), which provides automated accessibility remediation for websites. By accepting this agreement, you commit to using the Service responsibly and in accordance with applicable laws and ethical standards.

## Acceptable Use

### 1. Authorized Use Only

You may only use the Service to remediate websites that you own, control, or have explicit authorization to modify. You must:

- Verify domain ownership through our verification process before remediating any website
- Only register websites under domains you have verified
- Ensure you have the legal right to modify the content you submit for remediation

### 2. Accessibility Commitment

The Service is designed to improve web accessibility for people with disabilities. You agree to:

- Use the remediated content to genuinely improve accessibility for users with disabilities
- Not use the Service to create misleading claims about accessibility compliance
- Understand that automated remediation is a tool to assist, not replace, comprehensive accessibility testing and human review
- Recognize that legal compliance (e.g., ADA, Section 508, WCAG) requires ongoing effort beyond automated fixes

### 3. Content Responsibility

You are solely responsible for:

- The content of websites you submit for remediation
- Ensuring your content does not violate any laws, regulations, or third-party rights
- Any consequences arising from the use of remediated content
- Maintaining appropriate backups of your original content

### 4. Prohibited Activities

You must not:

- Use the Service to remediate websites you do not own or have authorization to modify
- Attempt to circumvent domain verification or security measures
- Use the Service for any illegal, harmful, or malicious purposes
- Reverse engineer, decompile, or attempt to extract the source code of the Service
- Overload or attempt to disrupt the Service infrastructure
- Share your account credentials with unauthorized parties

## Data and Privacy

### 5. Data Processing

By using the Service, you acknowledge that:

- We will process the HTML content of websites you submit for remediation
- We may store remediated content and accessibility audit results
- We maintain audit trails of your actions for compliance and security purposes
- We process your data in accordance with our Privacy Policy

### 6. Confidentiality

You agree to:

- Keep your verification tokens and access credentials confidential
- Not share sensitive information about the Service's internal operations
- Report any security vulnerabilities responsibly

## Compliance and Legal

### 7. Legal Compliance

You represent and warrant that:

- You have the legal authority to accept this agreement on behalf of your organization
- Your use of the Service complies with all applicable laws and regulations
- You will not use the Service in any way that violates intellectual property rights

### 8. Audit Trail

You acknowledge that:

- We maintain comprehensive audit trails of ethics agreement acceptances
- We log domain verifications, remediations, and other significant actions
- These records may be used for compliance, security, and dispute resolution purposes

## Liability and Disclaimers

### 9. Service Limitations

You understand and agree that:

- Automated accessibility remediation has limitations and may not catch all issues
- The Service provides code-level fixes but does not guarantee full legal compliance
- You are responsible for comprehensive accessibility testing and validation
- We do not provide legal advice regarding accessibility compliance

### 10. No Warranty

The Service is provided "as is" without warranties of any kind, either express or implied. We do not warrant that:

- The Service will be uninterrupted or error-free
- All accessibility issues will be detected or fixed
- Remediated content will meet all legal accessibility requirements

### 11. Limitation of Liability

To the maximum extent permitted by law:

- We are not liable for any indirect, incidental, or consequential damages
- Our total liability shall not exceed the amount you paid for the Service
- You agree to indemnify us against claims arising from your use of the Service

## Changes and Termination

### 12. Agreement Updates

We may update this Ethics Agreement from time to time. When we do:

- We will notify you of material changes
- You must accept the new version to continue using the Service
- Continued use after notification constitutes acceptance

### 13. Termination

We may suspend or terminate your access if:

- You violate this Ethics Agreement
- We detect fraudulent or malicious activity
- Required by law or legal process

You may terminate your use of the Service at any time by ceasing to use it and deleting your account.

## Acceptance

By clicking "I Accept" or using the Service, you acknowledge that:

- You have read and understood this Ethics Agreement
- You agree to be bound by its terms
- You have the authority to accept on behalf of your organization
- You will use the Service responsibly and ethically

## Contact

If you have questions about this Ethics Agreement, please contact us at:  
**Email:** ethics@accessify.org

---

**Last Updated:** December 13, 2024  
**Version:** 1.0
"""
    
    # Check if agreement already exists
    existing = q("SELECT id FROM ethics_agreement WHERE version = %s", ('1.0',))
    if existing:
        print("  Ethics agreement v1.0 already exists.")
        return existing[0]['id']
    
    agreement_id = q(
        """
        INSERT INTO ethics_agreement (version, content, effective_date)
        VALUES (%s, %s, %s)
        """,
        ('1.0', content.strip(), datetime(2024, 12, 13))
    )
    
    print(f"  ✓ Created ethics agreement v1.0 (ID: {agreement_id})")
    return agreement_id


def seed_organizations():
    """Create mock organizations."""
    print("\nCreating organizations...")
    
    orgs = [
        {
            'name': 'Accessibility First Foundation',
            'email_domain': 'a11yfirst.org'
        },
        {
            'name': 'Disability Rights Coalition',
            'email_domain': 'disabilityrights.org'
        },
        {
            'name': 'Inclusive Tech Nonprofit',
            'email_domain': 'inclusivetech.org'
        },
        {
            'name': 'Vision Impairment Support Services',
            'email_domain': 'visionimpairment.org'
        }
    ]
    
    org_ids = []
    for org in orgs:
        # Check if org already exists
        existing = q("SELECT id FROM organization WHERE email_domain = %s", (org['email_domain'],))
        if existing:
            print(f"  Organization '{org['name']}' already exists.")
            org_ids.append(existing[0]['id'])
            continue
        
        org_id = q(
            "INSERT INTO organization (name, email_domain) VALUES (%s, %s)",
            (org['name'], org['email_domain'])
        )
        org_ids.append(org_id)
        print(f"  ✓ Created: {org['name']} (ID: {org_id})")
    
    return org_ids


def seed_users(org_ids):
    """Create mock users for each organization."""
    print("\nCreating users...")
    
    # Default password for all test users
    default_password = "TestPassword123!"
    password_hash = hash_password(default_password)
    
    users = [
        {
            'organization_id': org_ids[0],
            'email': 'admin@a11yfirst.org',
            'full_name': 'Alice Anderson',
            'is_verified': True
        },
        {
            'organization_id': org_ids[0],
            'email': 'developer@a11yfirst.org',
            'full_name': 'Bob Builder',
            'is_verified': True
        },
        {
            'organization_id': org_ids[1],
            'email': 'coordinator@disabilityrights.org',
            'full_name': 'Carol Coordinator',
            'is_verified': True
        },
        {
            'organization_id': org_ids[2],
            'email': 'tech@inclusivetech.org',
            'full_name': 'David Developer',
            'is_verified': True
        },
        {
            'organization_id': org_ids[3],
            'email': 'manager@visionimpairment.org',
            'full_name': 'Eve Manager',
            'is_verified': False,
            'verification_token': generate_verification_token(),
            'verification_token_expires': datetime.now() + timedelta(days=7)
        }
    ]
    
    user_ids = []
    for user in users:
        # Check if user already exists
        existing = q("SELECT id FROM user WHERE email = %s", (user['email'],))
        if existing:
            print(f"  User '{user['email']}' already exists.")
            user_ids.append(existing[0]['id'])
            continue
        
        user_id = q(
            """
            INSERT INTO user 
            (organization_id, email, password_hash, full_name, is_verified, 
             verification_token, verification_token_expires)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user['organization_id'],
                user['email'],
                password_hash,
                user['full_name'],
                user['is_verified'],
                user.get('verification_token'),
                user.get('verification_token_expires')
            )
        )
        user_ids.append(user_id)
        status = "✓ (verified)" if user['is_verified'] else "○ (unverified)"
        print(f"  {status} Created: {user['email']} (ID: {user_id})")
    
    print(f"\n  Default password for all users: {default_password}")
    return user_ids


def seed_domains(org_ids):
    """Create verified domains for organizations."""
    print("\nCreating domains...")
    
    domains = [
        {
            'organization_id': org_ids[0],
            'domain_name': 'a11yfirst.org',
            'is_verified': True,
            'verification_method': 'meta_tag',
            'verified_at': datetime.now() - timedelta(days=30)
        },
        {
            'organization_id': org_ids[0],
            'domain_name': 'resources.a11yfirst.org',
            'is_verified': True,
            'verification_method': 'wellknown',
            'verified_at': datetime.now() - timedelta(days=15)
        },
        {
            'organization_id': org_ids[1],
            'domain_name': 'disabilityrights.org',
            'is_verified': True,
            'verification_method': 'meta_tag',
            'verified_at': datetime.now() - timedelta(days=20)
        },
        {
            'organization_id': org_ids[2],
            'domain_name': 'inclusivetech.org',
            'is_verified': True,
            'verification_method': 'wellknown',
            'verified_at': datetime.now() - timedelta(days=10)
        },
        {
            'organization_id': org_ids[3],
            'domain_name': 'visionimpairment.org',
            'is_verified': False,
            'verification_method': None,
            'verified_at': None
        }
    ]
    
    domain_ids = []
    for domain in domains:
        # Check if domain already exists
        existing = q(
            "SELECT id FROM domain WHERE organization_id = %s AND domain_name = %s",
            (domain['organization_id'], domain['domain_name'])
        )
        if existing:
            print(f"  Domain '{domain['domain_name']}' already exists.")
            domain_ids.append(existing[0]['id'])
            continue
        
        verification_token = generate_verification_token()
        
        domain_id = q(
            """
            INSERT INTO domain 
            (organization_id, domain_name, verification_token, is_verified, 
             verification_method, verified_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                domain['organization_id'],
                domain['domain_name'],
                verification_token,
                domain['is_verified'],
                domain['verification_method'],
                domain['verified_at']
            )
        )
        domain_ids.append(domain_id)
        status = "✓ (verified)" if domain['is_verified'] else "○ (unverified)"
        print(f"  {status} Created: {domain['domain_name']} (ID: {domain_id})")
        if not domain['is_verified']:
            print(f"      Token: {verification_token}")
    
    return domain_ids


def seed_ethics_acceptances(user_ids):
    """Record ethics agreement acceptances for verified users."""
    print("\nRecording ethics acceptances...")
    
    # First 4 users have accepted the agreement
    for i in range(min(4, len(user_ids))):
        user_id = user_ids[i]
        
        # Check if already accepted
        existing = q(
            "SELECT id FROM ethics_acceptance WHERE user_id = %s AND agreement_version = %s",
            (user_id, '1.0')
        )
        if existing:
            print(f"  User {user_id} has already accepted v1.0")
            continue
        
        q(
            """
            INSERT INTO ethics_acceptance (user_id, agreement_version, ip_address)
            VALUES (%s, %s, %s)
            """,
            (user_id, '1.0', '127.0.0.1')
        )
        print(f"  ✓ User {user_id} accepted ethics agreement v1.0")


def seed_websites(user_ids, domain_ids):
    """Create sample websites for testing."""
    print("\nCreating sample websites...")
    
    websites = [
        {
            'user_id': user_ids[0],
            'domain_id': domain_ids[0],
            'entry_url': 'https://a11yfirst.org',
            'name': 'Main Website',
            'status': 'registered'
        },
        {
            'user_id': user_ids[0],
            'domain_id': domain_ids[1],
            'entry_url': 'https://resources.a11yfirst.org/guides',
            'name': 'Resource Guides',
            'status': 'registered'
        },
        {
            'user_id': user_ids[2],
            'domain_id': domain_ids[2],
            'entry_url': 'https://disabilityrights.org',
            'name': 'DRC Homepage',
            'status': 'registered'
        }
    ]
    
    website_ids = []
    for website in websites:
        # Check if website already exists
        existing = q(
            "SELECT id FROM website WHERE user_id = %s AND entry_url = %s",
            (website['user_id'], website['entry_url'])
        )
        if existing:
            print(f"  Website '{website['name']}' already exists.")
            website_ids.append(existing[0]['id'])
            continue
        
        website_id = q(
            """
            INSERT INTO website (user_id, domain_id, entry_url, name, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                website['user_id'],
                website['domain_id'],
                website['entry_url'],
                website['name'],
                website['status']
            )
        )
        website_ids.append(website_id)
        print(f"  ✓ Created: {website['name']} (ID: {website_id})")
    
    return website_ids


def seed_sample_remediations(website_ids):
    """Create sample remediation data (pages with issues)."""
    print("\nCreating sample remediation data...")
    
    import json
    
    # Sample HTML content with accessibility issues
    sample_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sample Accessible Page</title>
</head>
<body>
    <h1>Welcome to Our Nonprofit</h1>
    <img src="logo.png" alt="Organization logo">
    <p>We are committed to accessibility for all users.</p>
    <button aria-label="Learn more about our mission">Learn More</button>
    <nav role="navigation">
        <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
        </ul>
    </nav>
</body>
</html>"""
    
    # Create a sample remediated page for the first website
    if website_ids:
        website_id = website_ids[0]
        
        # Check if page already exists
        existing = q("SELECT id FROM page WHERE website_id = %s", (website_id,))
        if existing:
            print(f"  Sample page already exists for website {website_id}")
            page_id = existing[0]['id']
        else:
            page_id = q(
                """
                INSERT INTO page (url, raw_html, fixed_html, status, website_id)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    'https://a11yfirst.org',
                    sample_html,
                    sample_html,  # In real scenario, this would be the fixed version
                    'complete',
                    website_id
                )
            )
            print(f"  ✓ Created sample page (ID: {page_id})")
        
        # Create sample issues
        sample_issues = [
            {
                'type': 'color-contrast',
                'severity': 'serious',
                'description': 'Elements must have sufficient color contrast',
                'help_url': 'https://dequeuniversity.com/rules/axe/4.4/color-contrast',
                'fixed': True
            },
            {
                'type': 'image-alt',
                'severity': 'critical',
                'description': 'Images must have alternate text',
                'help_url': 'https://dequeuniversity.com/rules/axe/4.4/image-alt',
                'fixed': True
            },
            {
                'type': 'button-name',
                'severity': 'critical',
                'description': 'Buttons must have discernible text',
                'help_url': 'https://dequeuniversity.com/rules/axe/4.4/button-name',
                'fixed': True
            },
            {
                'type': 'landmark-one-main',
                'severity': 'moderate',
                'description': 'Document should have one main landmark',
                'help_url': 'https://dequeuniversity.com/rules/axe/4.4/landmark-one-main',
                'fixed': True
            }
        ]
        
        for issue in sample_issues:
            # Check if issue already exists
            existing = q(
                "SELECT id FROM issue WHERE page_id = %s AND type = %s",
                (page_id, issue['type'])
            )
            if existing:
                continue
            
            # Store details as JSON matching the actual schema
            details = {
                'description': issue['description'],
                'help_url': issue['help_url'],
                'fixed': issue['fixed']
            }
            
            q(
                """
                INSERT INTO issue (page_id, type, severity, details)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    page_id,
                    issue['type'],
                    issue['severity'],
                    json.dumps(details)
                )
            )
        
        print(f"  ✓ Created {len(sample_issues)} sample issues for page {page_id}")
        
        # Create sample chunks for RAG
        sample_chunks = [
            {
                'path': '/html/body/h1',
                'role': 'heading',
                'text': 'Welcome to Our Nonprofit. We are committed to accessibility for all users.',
                'attrs': {'level': 1}
            },
            {
                'path': '/html/body/p',
                'role': 'paragraph',
                'text': 'Our organization provides services to people with disabilities.',
                'attrs': {}
            },
            {
                'path': '/html/body/button',
                'role': 'button',
                'text': 'Learn more about our mission to create an inclusive digital world.',
                'attrs': {'aria-label': 'Learn more about our mission'}
            },
            {
                'path': '/html/body/nav',
                'role': 'navigation',
                'text': 'Contact us for more information about our accessibility initiatives.',
                'attrs': {}
            }
        ]
        
        for chunk_data in sample_chunks:
            # Check if chunk already exists
            existing = q(
                "SELECT id FROM chunk WHERE page_id = %s AND path = %s",
                (page_id, chunk_data['path'])
            )
            if existing:
                continue
            
            # Create a simple embedding (in real scenario, this would be from OpenAI)
            # For seed data, we'll use a placeholder
            embedding = [0.0] * 1536  # text-embedding-3-small dimension
            embedding_json = json.dumps(embedding)
            
            q(
                """
                INSERT INTO chunk (page_id, path, role, text, attrs, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (page_id, chunk_data['path'], chunk_data['role'], chunk_data['text'], 
                 json.dumps(chunk_data['attrs']), embedding_json)
            )
        
        print(f"  ✓ Created {len(sample_chunks)} sample chunks for RAG")
        
        # Update website status
        q(
            "UPDATE website SET status = %s, last_remediation_at = %s WHERE id = %s",
            ('remediated', datetime.now(), website_id)
        )
        print(f"  ✓ Updated website {website_id} status to 'remediated'")


def seed_audit_logs(user_ids, domain_ids, website_ids):
    """Create sample audit log entries."""
    print("\nCreating audit log entries...")
    
    # Log domain verifications
    for i in range(min(4, len(domain_ids))):
        domain_id = domain_ids[i]
        user_id = user_ids[min(i, len(user_ids) - 1)]
        
        domain_info = q("SELECT domain_name, verification_method FROM domain WHERE id = %s", (domain_id,))
        if domain_info and domain_info[0]['verification_method']:
            # Check if already logged
            existing = q(
                "SELECT id FROM audit_log WHERE event_type = %s AND details LIKE %s",
                ('domain_verified', f'%"domain_id": {domain_id}%')
            )
            if existing:
                continue
            
            q(
                """
                INSERT INTO audit_log (event_type, user_id, details, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    'domain_verified',
                    user_id,
                    f'{{"domain_id": {domain_id}, "domain": "{domain_info[0]["domain_name"]}", "method": "{domain_info[0]["verification_method"]}"}}',
                    '127.0.0.1'
                )
            )
            print(f"  ✓ Logged domain verification for domain {domain_id}")
    
    # Log remediation for first website
    if website_ids:
        website_id = website_ids[0]
        user_id = user_ids[0]
        
        # Check if already logged
        existing = q(
            "SELECT id FROM audit_log WHERE event_type = %s AND details LIKE %s",
            ('remediation_completed', f'%"website_id": {website_id}%')
        )
        if not existing:
            q(
                """
                INSERT INTO audit_log (event_type, user_id, details, ip_address)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    'remediation_completed',
                    user_id,
                    f'{{"website_id": {website_id}, "issues_found": 4, "issues_fixed": 4}}',
                    '127.0.0.1'
                )
            )
            print(f"  ✓ Logged remediation for website {website_id}")


def main():
    """Run all seed data functions."""
    print("=" * 60)
    print("Accessify Seed Data Script")
    print("=" * 60)
    
    try:
        # Seed in dependency order
        seed_ethics_agreement()
        org_ids = seed_organizations()
        user_ids = seed_users(org_ids)
        domain_ids = seed_domains(org_ids)
        seed_ethics_acceptances(user_ids)
        website_ids = seed_websites(user_ids, domain_ids)
        seed_sample_remediations(website_ids)
        seed_audit_logs(user_ids, domain_ids, website_ids)
        
        print("\n" + "=" * 60)
        print("✓ Seed data created successfully!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  Email: admin@a11yfirst.org")
        print("  Password: TestPassword123!")
        print("\nOther test users:")
        print("  - developer@a11yfirst.org")
        print("  - coordinator@disabilityrights.org")
        print("  - tech@inclusivetech.org")
        print("  (All use the same password)")
        print("\nSample Data:")
        print("  - 4 organizations with different domains")
        print("  - 5 users (4 verified, 1 unverified)")
        print("  - 5 domains (4 verified, 1 unverified)")
        print("  - 3 registered websites")
        print("  - 1 remediated website with sample issues and chunks")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        raise


if __name__ == "__main__":
    main()
