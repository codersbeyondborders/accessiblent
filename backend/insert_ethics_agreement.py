#!/usr/bin/env python3
"""
Script to insert the initial v1.0 ethics agreement into the database.
Run this once after database setup to create the first ethics agreement.
"""

import datetime
from db import init_pool, q

# Ethics Agreement v1.0 Content
ETHICS_AGREEMENT_V1_CONTENT = """
# Accessify Ethics Agreement

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


def insert_initial_ethics_agreement():
    """
    Insert the v1.0 ethics agreement into the database.
    """
    init_pool()
    
    # Check if v1.0 already exists
    existing = q("SELECT id FROM ethics_agreement WHERE version=%s", ("1.0",))
    
    if existing:
        print("Ethics agreement v1.0 already exists in the database.")
        print(f"Agreement ID: {existing[0]['id']}")
        return
    
    # Insert the agreement
    effective_date = datetime.datetime(2024, 12, 13, 0, 0, 0)
    
    agreement_id = q(
        """INSERT INTO ethics_agreement (version, content, effective_date, created_at)
           VALUES (%s, %s, %s, %s)""",
        ("1.0", ETHICS_AGREEMENT_V1_CONTENT.strip(), effective_date, datetime.datetime.utcnow())
    )
    
    print(f"Successfully inserted ethics agreement v1.0")
    print(f"Agreement ID: {agreement_id}")
    print(f"Effective Date: {effective_date}")
    print(f"Content length: {len(ETHICS_AGREEMENT_V1_CONTENT)} characters")
    
    # Verify insertion
    verify = q("SELECT * FROM ethics_agreement WHERE id=%s", (agreement_id,))
    if verify:
        print("\nVerification successful:")
        print(f"  Version: {verify[0]['version']}")
        print(f"  Effective Date: {verify[0]['effective_date']}")
        print(f"  Created At: {verify[0]['created_at']}")
    else:
        print("\nWarning: Could not verify insertion")


if __name__ == "__main__":
    insert_initial_ethics_agreement()
