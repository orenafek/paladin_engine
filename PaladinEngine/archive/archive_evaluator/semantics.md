# PaLaDiN DSL Semantics

## Operators

### Basic Logical Operators
- And
- Or
- Not

## Basic Temporal Operators
- Finally
- Globally
- Next
- Until
- Release

### New Temporal Operators

- Before: A Happened Before B
   ```math
  B(ϕ, ψ) := ∃i >= 0, ω_i ⊨ ψ, ∃k, 0 <= k <= i, ω_k ⊨ ϕ <==>
  B(ϕ, ψ) := U(¬G(¬ϕ), ψ)
  ```