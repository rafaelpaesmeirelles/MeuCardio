import assert from "node:assert/strict";
import test from "node:test";
import { canUseCommercialFeature, canCheckout, checkoutLocation, formatBRL, planCredit } from "../src/lib/commercialPlans.ts";

test("access follows server entitlements, including legacy benefits and administrative grants", () => {
  assert.equal(canUseCommercialFeature({ plano: "completo" }, "ai"), false);
  assert.equal(canUseCommercialFeature({ plano: "basico", entitlements: { ai: true, mail: false, source: "legacy" } }, "ai"), true);
  assert.equal(canUseCommercialFeature({ plano: "ia", entitlements: { ai: false } }, "ai"), false);
  assert.equal(canUseCommercialFeature(null, "mail"), false);
});

test("prelaunch and unavailable checkout cannot be opened", () => {
  const plan = { id: "ia", checkout_available: true };
  assert.equal(canCheckout({ subscriptions_enabled: false, checkout_available: true }, plan), false);
  assert.equal(canCheckout({ subscriptions_enabled: true }, { id: "ia" }), false);
  assert.equal(canCheckout({ subscriptions_enabled: true, checkout_available: true }, { checkout_available: false }), false);
  assert.equal(canCheckout({ subscriptions_enabled: true, checkout_available: true }, plan), true);
});

test("credit reflects server configuration and does not attach to plans without AI", () => {
  assert.equal(planCredit({ ai_monthly_credit_centavos: 4000 }, { features: { ai: false }, ai_monthly_credit_centavos: 4000 }), null);
  assert.equal(planCredit({}, { features: { ai: true }, ai_monthly_credit_centavos: 4000 }), 4000);
  assert.equal(planCredit({ ai_monthly_credit_centavos: 5000 }, { features: { ai: true } }), 5000);
  assert.equal(planCredit({}, { features: { ai: true } }), null);
  assert.match(formatBRL(9990), /99,90/);
});

test("checkout never redirects to empty, insecure or executable URLs", () => {
  for (const url of [null, undefined, "", "javascript:alert(1)", "http://example.com", "https://example.com", "/checkout"]) {
    assert.throws(() => checkoutLocation(url));
  }
  assert.equal(checkoutLocation("https://checkout.stripe.com/c/pay/session"), "https://checkout.stripe.com/c/pay/session");
});
