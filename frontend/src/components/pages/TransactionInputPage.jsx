import React, { useState, useEffect } from 'react';
import { 
  Search, 
  CreditCard, 
  MapPin, 
  Smartphone, 
  AlertCircle, 
  ChevronDown, 
  ChevronUp, 
  SlidersHorizontal,
  RefreshCw,
  Sparkles
} from 'lucide-react';
import { usePersona } from '../../context/PersonaContext';
import { useAuth } from '../../context/AuthContext';
import transactionService from '../../services/transactionService';

const CITIES = [
  'Mumbai',
  'Delhi',
  'Bangalore',
  'Hyderabad',
  'Chennai',
  'Kolkata',
  'Pune',
  'New York',
  'London',
  'Singapore',
  'Tokyo',
  'Dubai',
  'San Francisco',
  'Sydney',
  'Frankfurt',
  'Toronto'
];

const PAYMENT_METHODS = [
  { id: 'credit_card', label: 'Credit Card (Visa / Mastercard)' },
  { id: 'debit_card', label: 'Debit Card' },
  { id: 'upi', label: 'UPI / Instant Bank Transfer' },
  { id: 'wire_transfer', label: 'Bank Wire Transfer' },
];

const MERCHANT_CATEGORIES = [
  { id: 'grocery', label: 'Groceries & Daily Essentials' },
  { id: 'general', label: 'General Shopping' },
  { id: 'electronics', label: 'Electronics & Computers' },
  { id: 'luxury', label: 'Luxury Goods & Jewelry' },
  { id: 'travel', label: 'Travel, Flights & Hotels' },
  { id: 'entertainment', label: 'Entertainment & Gaming' },
];

const PRESETS = [
  {
    label: 'Everyday Grocery (Safe)',
    desc: '$42.50 in Mumbai from familiar device',
    data: {
      amount: 42.50,
      currency: 'USD',
      payment_method: 'credit_card',
      location_city: 'Mumbai',
      is_device_familiar: true,
      merchant_category: 'grocery',
      card_network: 'Visa',
      user_identifier: 'USR-8821'
    }
  },
  {
    label: 'Online Electronics (Review Needed)',
    desc: '$750.00 in Bangalore from a new device',
    data: {
      amount: 750.00,
      currency: 'USD',
      payment_method: 'credit_card',
      location_city: 'Bangalore',
      is_device_familiar: false,
      merchant_category: 'electronics',
      card_network: 'Mastercard',
      user_identifier: 'USR-8821'
    }
  },
  {
    label: 'Late-Night Luxury (High Risk)',
    desc: '$4,800.00 in Dubai from a new device',
    data: {
      amount: 4800.00,
      currency: 'USD',
      payment_method: 'credit_card',
      location_city: 'Dubai',
      is_device_familiar: false,
      merchant_category: 'luxury',
      card_network: 'Visa',
      user_identifier: 'USR-8821'
    }
  },
  {
    label: 'Impossible Travel (Very High Risk)',
    desc: '$16,500.00 in Tokyo (too fast to be real travel)',
    data: {
      amount: 16500.00,
      currency: 'USD',
      payment_method: 'wire_transfer',
      location_city: 'Tokyo',
      is_device_familiar: false,
      merchant_category: 'luxury',
      card_network: 'Visa',
      user_identifier: 'USR-8821'
    }
  }
];

export const TransactionInputPage = ({ onAnalysisComplete }) => {
  const { isAnalyst } = usePersona();
  const { user, isAuthenticated } = useAuth();

  // Core Form State - empty by default on fresh session
  const [amount, setAmount] = useState('');
  const [currency, setCurrency] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [locationCity, setLocationCity] = useState('');
  const [isDeviceFamiliar, setIsDeviceFamiliar] = useState(null); // null = unselected
  const [merchantCategory, setMerchantCategory] = useState('');

  // Optional Account & Technical Parameters - empty by default
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [userId, setUserId] = useState('');
  const [cardNetwork, setCardNetwork] = useState('');
  const [deviceId, setDeviceId] = useState('');
  const [ipAddress, setIpAddress] = useState('');

  // Execution State
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState(null);

  // Always reset fields to empty when this view is navigated to or mounted
  useEffect(() => {
    setAmount('');
    setCurrency('');
    setPaymentMethod('');
    setLocationCity('');
    setIsDeviceFamiliar(null);
    setMerchantCategory('');
    setUserId('');
    setCardNetwork('');
    setDeviceId('');
    setIpAddress('');
    setFormError(null);
  }, []);

  const applyPreset = (preset) => {
    setAmount(String(preset.data.amount));
    setCurrency(preset.data.currency || 'USD');
    setPaymentMethod(preset.data.payment_method);
    setLocationCity(preset.data.location_city);
    setIsDeviceFamiliar(preset.data.is_device_familiar);
    setMerchantCategory(preset.data.merchant_category || 'general');
    if (preset.data.card_network) setCardNetwork(preset.data.card_network);
    if (preset.data.user_identifier) setUserId(preset.data.user_identifier);
    setFormError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);

    const parsedAmount = parseFloat(amount);
    if (!amount || isNaN(parsedAmount) || parsedAmount <= 0) {
      setFormError('Please enter a valid amount greater than $0.00.');
      return;
    }
    if (parsedAmount > 100000000) {
      setFormError('Amount exceeds maximum transaction limit ($100,000,000).');
      return;
    }
    if (!currency) {
      setFormError('Please select a currency.');
      return;
    }
    if (!paymentMethod) {
      setFormError('Please select a payment method.');
      return;
    }
    if (!locationCity) {
      setFormError('Please select a city.');
      return;
    }
    if (isDeviceFamiliar === null) {
      setFormError('Please select whether this is a known device (Yes or No).');
      return;
    }

    const payload = {
      amount: parsedAmount,
      payment_method: paymentMethod,
      location_city: locationCity,
      is_device_familiar: Boolean(isDeviceFamiliar),
      transaction_timestamp: new Date().toISOString(),
      advanced_details: {
        user_identifier: userId.trim() || (isAuthenticated ? user?.user_identifier : undefined),
        currency: currency,
        card_network: cardNetwork || undefined,
        merchant_category: merchantCategory || 'general',
        device_id: deviceId.trim() || undefined,
        ip_address: ipAddress.trim() || '127.0.0.1'
      }
    };

    setIsLoading(true);
    try {
      const result = await transactionService.analyzeTransaction(payload);
      setIsLoading(false);
      onAnalysisComplete(result);
    } catch (err) {
      setIsLoading(false);
      setFormError(
        err.message || 'Unable to check transaction. Please ensure the backend server is running.'
      );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-2 select-none">
      
      {/* Page Title & Context Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1D3A1E]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white font-sans">
            Check a Transaction
          </h1>
          <p className="text-xs sm:text-sm text-[#8A998A] mt-1">
            Enter payment information to see if it is safe, needs review, or should be stopped.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {isAuthenticated && (
            <span className="text-xs font-mono px-3 py-1 rounded-md bg-[#0A120B] text-[#A0FF99] border border-[#1D3A1E] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#A0FF99]" />
              Personal Ledger Active
            </span>
          )}
          <span className="text-xs font-mono px-3 py-1 rounded-md bg-[#1D3A1E] text-white">
            View Mode: <strong className="text-[#A0FF99]">{isAnalyst ? 'Analyst' : 'Standard'}</strong>
          </span>
        </div>
      </div>

      {/* Quick Test Presets */}
      <div className="space-y-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-[#8A998A] font-mono">
          <Sparkles className="w-3.5 h-3.5 text-[#A0FF99]" />
          <span>Quick Example Scenarios (Click to test)</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {PRESETS.map((p, i) => (
            <button
              key={i}
              type="button"
              onClick={() => applyPreset(p)}
              className="text-left p-3.5 rounded-xl border border-[#1D3A1E] bg-[#0A120B] hover:bg-[#122314] hover:border-[#A0FF99]/40 transition-all text-xs space-y-1"
            >
              <div className="font-semibold text-white">
                {p.label}
              </div>
              <div className="text-[11px] text-[#8A998A] font-mono truncate">{p.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Error Alert Banner */}
      {formError && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex items-start gap-3 text-xs leading-relaxed">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
          <div className="flex-1">
            <strong className="font-semibold block text-rose-200">Unable to Complete Check</strong>
            {formError}
          </div>
        </div>
      )}

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Section 1: Financial & Payment Parameters */}
        <div className="p-6 sm:p-7 rounded-xl fintech-card space-y-5">
          <div className="flex items-center gap-2.5 pb-3 border-b border-[#1D3A1E]">
            <CreditCard className="w-4 h-4 text-[#A0FF99]" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              1. Payment Information
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            {/* Amount */}
            <div className="sm:col-span-2 space-y-2">
              <label className="text-xs font-semibold text-white">
                Transaction Amount <span className="text-[#A0FF99]">*</span>
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-sm font-mono font-bold text-[#8A998A]">
                  $
                </span>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="e.g. 150.00"
                  className="w-full pl-8 pr-4 py-2.5 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-sm font-mono focus:outline-none focus:border-[#A0FF99] transition-colors"
                />
              </div>
              <span className="text-[11px] text-[#8A998A] block">
                How much is being sent or spent in this transaction.
              </span>
            </div>

            {/* Currency */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-white">
                Currency <span className="text-[#A0FF99]">*</span>
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-sm font-mono focus:outline-none focus:border-[#A0FF99]"
              >
                <option value="" disabled>Select Currency</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="INR">INR (₹)</option>
                <option value="GBP">GBP (£)</option>
              </select>
            </div>

            {/* Payment Rail */}
            <div className="sm:col-span-2 space-y-2">
              <label className="text-xs font-semibold text-white">
                Payment Method <span className="text-[#A0FF99]">*</span>
              </label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-sm focus:outline-none focus:border-[#A0FF99]"
              >
                <option value="" disabled>Select Payment Method</option>
                {PAYMENT_METHODS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Merchant Category */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-white">
                Store or Service Type
              </label>
              <select
                value={merchantCategory}
                onChange={(e) => setMerchantCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-sm focus:outline-none focus:border-[#A0FF99]"
              >
                <option value="">Select Store or Service Type</option>
                {MERCHANT_CATEGORIES.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Location & Device */}
        <div className="p-6 sm:p-7 rounded-xl fintech-card space-y-5">
          <div className="flex items-center gap-2.5 pb-3 border-b border-[#1D3A1E]">
            <MapPin className="w-4 h-4 text-[#A0FF99]" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              2. Location & Device
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
            {/* Location City */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-white">
                Where is this payment being initiated? (City) <span className="text-[#A0FF99]">*</span>
              </label>
              <select
                value={locationCity}
                onChange={(e) => setLocationCity(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-sm focus:outline-none focus:border-[#A0FF99]"
              >
                <option value="" disabled>Select City</option>
                {CITIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <span className="text-[11px] text-[#8A998A] block">
                Used to verify travel speed against the account's recent locations.
              </span>
            </div>

            {/* Device Security Status Toggle */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-white">
                Is this a known device? <span className="text-[#A0FF99]">*</span>
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setIsDeviceFamiliar(true)}
                  className={`p-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    isDeviceFamiliar === true
                      ? 'bg-[#1D3A1E] text-[#A0FF99] border-[#A0FF99]/40'
                      : 'bg-[#020202] text-[#8A998A] border-[#1D3A1E] hover:text-white'
                  }`}
                >
                  <Smartphone className="w-4 h-4" />
                  <span>Yes (Known Device)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setIsDeviceFamiliar(false)}
                  className={`p-3 rounded-lg border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    isDeviceFamiliar === false
                      ? 'bg-rose-500/20 text-rose-400 border-rose-500/40'
                      : 'bg-[#020202] text-[#8A998A] border-[#1D3A1E] hover:text-white'
                  }`}
                >
                  <Smartphone className="w-4 h-4" />
                  <span>No (New / Unfamiliar)</span>
                </button>
              </div>
              <span className="text-[11px] text-[#8A998A] block">
                {isDeviceFamiliar === null
                  ? 'Please select whether this payment is being made from a known device.'
                  : isDeviceFamiliar
                  ? 'Device marked as recognized and used safely before.'
                  : 'Device marked as brand-new or unrecognized.'}
              </span>
            </div>
          </div>
        </div>

        {/* Section 3: Optional Account Details */}
        <div className="rounded-xl fintech-card overflow-hidden">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="w-full px-6 py-4 flex items-center justify-between bg-[#0A120B] hover:bg-[#122314] transition-colors text-left"
          >
            <div className="flex items-center gap-2.5">
              <SlidersHorizontal className="w-4 h-4 text-[#A0FF99]" />
              <span className="text-xs font-bold uppercase tracking-wider text-white font-mono">
                Account & Technical Details (Optional)
              </span>
            </div>
            {showAdvanced ? (
              <ChevronUp className="w-4 h-4 text-[#8A998A]" />
            ) : (
              <ChevronDown className="w-4 h-4 text-[#8A998A]" />
            )}
          </button>

          {showAdvanced && (
            <div className="p-6 border-t border-[#1D3A1E] space-y-4 bg-[#060B06]">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-white">
                    Account ID / Username (Optional)
                  </label>
                  <input
                    type="text"
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    placeholder="e.g. USR-8821"
                    className="w-full px-3 py-2 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-xs font-mono focus:outline-none focus:border-[#A0FF99]"
                  />
                  <span className="text-[10px] text-[#8A998A]">
                    Links to your typical spending history to understand what is normal for you.
                  </span>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-white">
                    Card Network (Optional)
                  </label>
                  <select
                    value={cardNetwork}
                    onChange={(e) => setCardNetwork(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-xs focus:outline-none focus:border-[#A0FF99]"
                  >
                    <option value="">Select Card Network (Optional)</option>
                    <option value="Visa">Visa</option>
                    <option value="Mastercard">Mastercard</option>
                    <option value="Amex">American Express</option>
                    <option value="Discover">Discover</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-white">
                    Device Identifier (Optional)
                  </label>
                  <input
                    type="text"
                    value={deviceId}
                    onChange={(e) => setDeviceId(e.target.value)}
                    placeholder="e.g. DEV-89A"
                    className="w-full px-3 py-2 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-xs font-mono focus:outline-none focus:border-[#A0FF99]"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-white">
                    IP Address (Optional)
                  </label>
                  <input
                    type="text"
                    value={ipAddress}
                    onChange={(e) => setIpAddress(e.target.value)}
                    placeholder="e.g. 127.0.0.1"
                    className="w-full px-3 py-2 rounded-lg border border-[#1D3A1E] bg-[#020202] text-white text-xs font-mono focus:outline-none focus:border-[#A0FF99]"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Submit Action Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
          <button
            type="button"
            onClick={() => {
              setAmount('');
              setCurrency('');
              setPaymentMethod('');
              setLocationCity('');
              setIsDeviceFamiliar(null);
              setMerchantCategory('');
              setUserId('');
              setCardNetwork('');
              setDeviceId('');
              setIpAddress('');
              setFormError(null);
            }}
            className="text-xs font-mono text-[#8A998A] hover:text-white flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset All Fields</span>
          </button>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg text-sm font-semibold bg-[#A0FF99] hover:bg-[#B8FFB3] text-[#020202] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Checking Safety Rules & Models...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Check This Transaction</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TransactionInputPage;