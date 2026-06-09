
# Red Dot - Positioning (Stage 0)

> **Stage 0 of 8 — Red Dot pipeline.**
> next: [case intake](1-case-intake.md) →
> Shared nodes: [spec schema](../concepts/spec-schema.md), [the gate machinery](../concepts/the-gates.md)

The offer-first cut. Before modeling anything, decide what the assessment is *for*, who the customer is, and which transition the expert is paid to move people through. The lifecycle map gets cut to fit the offer, so this comes first.

## Contract

- **Consumes:** the expert's offer, who buys, and the problem they pay to have solved.
- **Produces:** a positioning brief: customer, offer, the transitions worth money, and the voice + banned-phrase list.
- **Owes the rest of the system:** the joints the map will be cut at (Stage 2) and the voice constraints (Stage 6, the voice gate).

## Method

Interview the expert for the commercial frame, not the method (the method comes
in Stage 1). Ask, in plain language:
- Who is the customer, and what do they call their problem before they meet you?
- What do you sell, and what transition does buying it move them through?
- At what point does someone become willing to pay? What changed for them?
- What words and claims must never appear (competitors, hype, anything off-brand)?

The single most useful answer is the *transition worth money*. The lifecycle map
(Stage 2) will be cut so its stage boundaries line up with that transition,
because the boundaries are what the expert sells.

## Craft rules and failure modes

- This is a COMMERCIAL read, kept separate from the epistemic case walk in
  Stage 1. Don't try to extract the model here.
- The failure mode is cutting the map at academically-true joints that aren't
  where money changes hands. A map that's accurate but commercially inert leads
  nowhere. Accuracy on the boundaries, but the boundaries follow the offer.
- Capture banned phrases now; the voice gate at Stage 6 enforces them.

## Output — what you write into `spec.json`

```
spec.positioning = {
  "customer": "...",
  "offer": {"what": "...", "transition_sold": "..."},
  "transitions_worth_money": ["..."],
  "voice": "short description of tone",
  "banned_phrases": ["here's the thing", "nobody talks about", "..."]
}
```
Also seed `spec.banned_phrases` (Stage 6 and the gate-checker read it).

## Gates this stage must satisfy

- **Commercial closure** (activates at assembly once an offer is declared):
  every stage boundary must map to something the expert offers. You are setting
  up that gate here by naming the transitions worth money.

---
**Next stage:** [case intake](1-case-intake.md). Back to the [router](../SKILL.md).