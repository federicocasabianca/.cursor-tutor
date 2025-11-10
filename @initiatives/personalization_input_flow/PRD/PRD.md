# 🧩 Epic: Personalization Input Flow – Push vs Pull Strategy

## 1. Context

This epic is part of Eduki’s Q4 onboarding initiative focused on CRM-led behavioral activation. We are introducing a **Personalization Input Flow** for new users to set their subject and grade preferences.

The goal is to test two strategic approaches to gather user preferences and assess their downstream impact on engagement, onboarding effectiveness, and CRM personalization.

### Benchmarked Approaches:
- **E-commerce (Push):** Prompt users upfront during registration to input preferences.
- **Marketplace (Pull):** Wait for implicit signals; nudge users passively post-signup to personalize.

---

## 2. User Problem

New Eduki users receive **generic onboarding experiences** that fail to surface relevant materials or guide them toward high-value actions.  
This leads to:
- Low perceived relevance
- Missed opportunities for early engagement
- Drop-off before realizing Eduki’s value

---

## 3. Hypothesis

| Component | Hypothesis |
|----------|------------|
| **Cause** | Offering early preference input (Push) vs letting users opt in when ready (Pull) |
| **Effect** | Increases content relevance, engagement, and purchase conversion |
| **Rationale** | Tailored onboarding accelerates time-to-value and reinforces platform usefulness |

---

## 4. Solution: A/B Test

### Variant A – **Push Flow**
- 2-step onboarding: After email/password, user is prompted to enter **Fach** (subject) + **Klassenstufen** (grade)
- Input is **optional**, but screen **must be seen** before proceeding
- Homepage carousel reflects user preferences (fallback to generic if skipped)

### Variant B – **Pull Flow**
- No prompt during signup
- Subtle nudges shown after landing: 
  - Top banner (“Set preferences to personalize”)
  - Inline widget in wishlist page
  - Dismissible card with CTA
- User can update preferences at any time via profile

---

## 5. Metrics of Success

| Metric | Type       | Baseline | Target |
|--------|------------|----------|--------|
| % of users who complete personalization | Primary    | TBD      | Push: +25%, Pull: +10% |
| Homepage sessions with personalized content | Secondary  | TBD      | +15% |
| First purchase within 7 days | Secondary  | TBD      | +8% |
| Bounce after registration | Guardrail  | TBD      | No increase |
| Pre-purchase churn rate | Guardrail  | 60%      | ↓ by 10% |

---

## 6. Scope

### ✅ In Scope

- Personalization onboarding for **web-based new user flows**.
- **Trigger points by sign-up method:**
  - **Regular signup (email/password):** Intercept with personalization flow **immediately after clicking the yellow CTA** on the registration form.
  - **3rd-party platform signups (Google, Facebook, Apple, Microsoft):** Intercept **after user returns from provider and accepts Terms & Conditions** via popup.
- Banner and CTA logic for Pull variant (homepage and wishlist surface).
- Homepage carousel logic (personalized vs. default fallback).

### ❌ Out of Scope

- Mobile app onboarding
- CRM flows beyond initial confirmation
- Changes to registration form layout or T&C logic outside of trigger injection

---

## 7. Questions This Test Will Answer

- Does proactive prompting (Push) result in higher personalization completion?
- Does Pull avoid friction while still capturing useful data?
- How do these flows impact downstream engagement and conversion?
- What strategy best aligns with our web-first activation funnel?

---

## 8. Future Scenarios

| Scenario | Interpretation | Next Action |
|----------|----------------|-------------|
| ✅ **Significant results – Push wins** | Preference input is high, with no major bounce | Roll out Push onboarding to all new users |
| ✅ **Significant results – Pull wins** | Pull drives equal/better results with better UX | Adopt Pull and optimize nudging surfaces |
| ❌ **No significant difference** | Equal results, different UX impacts | Default to Pull (lower friction), or hybrid model |