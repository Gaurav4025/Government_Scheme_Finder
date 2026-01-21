import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Upload, Check, ChevronRight, ChevronLeft } from "lucide-react";
import { toast } from 'sonner';

export default function RegistrationForm({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    
    // Step 2: Personal Details
    mobileNumber: '',
    dateOfBirth: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    
    // Step 3: Documents
    documents: [],
  });

  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      if (file.size > 5 * 1024 * 1024) {
        toast.error(`File ${file.name} is too large (max 5MB)`);
        return;
      }
      setUploadedFiles(prev => [...prev, file]);
    });
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const validateStep = (step) => {
    switch(step) {
      case 1:
        if (!formData.firstName.trim()) {
          toast.error('First name is required');
          return false;
        }
        if (!formData.lastName.trim()) {
          toast.error('Last name is required');
          return false;
        }
        if (!formData.email.includes('@')) {
          toast.error('Valid email is required');
          return false;
        }
        if (formData.password.length < 6) {
          toast.error('Password must be at least 6 characters');
          return false;
        }
        if (formData.password !== formData.confirmPassword) {
          toast.error('Passwords do not match');
          return false;
        }
        return true;
      
      case 2:
        if (!formData.mobileNumber.trim()) {
          toast.error('Mobile number is required');
          return false;
        }
        if (!formData.dateOfBirth) {
          toast.error('Date of birth is required');
          return false;
        }
        if (!formData.address.trim()) {
          toast.error('Address is required');
          return false;
        }
        if (!formData.city.trim()) {
          toast.error('City is required');
          return false;
        }
        if (!formData.state.trim()) {
          toast.error('State is required');
          return false;
        }
        if (!formData.zipCode.trim()) {
          toast.error('Zip code is required');
          return false;
        }
        return true;
      
      case 3:
        if (uploadedFiles.length === 0) {
          toast.error('Please upload at least one document');
          return false;
        }
        return true;
      
      default:
        return true;
    }
  };

  const handleNextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handlePrevStep = () => {
    setCurrentStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setIsLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('Registration Data:', {
        ...formData,
        documents: uploadedFiles.map(f => f.name)
      });
      
      toast.success('Registration completed successfully!');
      setCurrentStep(4); // Go to confirmation page
      
      if (onComplete) {
        onComplete({
          ...formData,
          documents: uploadedFiles
        });
      }
    } catch (error) {
      toast.error('Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Step 1: Basic Information
  const Step1 = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-foreground">Basic Information</h2>
      <p className="text-sm text-muted-foreground">Let's start with your basic details</p>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="firstName" className="text-foreground">First Name</Label>
          <Input
            id="firstName"
            name="firstName"
            placeholder="John"
            value={formData.firstName}
            onChange={handleInputChange}
            className="mt-1 bg-background text-foreground border-border focus:border-primary"
            autoComplete="given-name"
          />
        </div>
        <div>
          <Label htmlFor="lastName" className="text-foreground">Last Name</Label>
          <Input
            id="lastName"
            name="lastName"
            placeholder="Doe"
            value={formData.lastName}
            onChange={handleInputChange}
            className="mt-1 bg-background text-foreground border-border focus:border-primary"
            autoComplete="family-name"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="email" className="text-foreground">Email Address</Label>
        <Input
          id="email"
          name="email"
          type="email"
          placeholder="john@example.com"
          value={formData.email}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="email"
        />
      </div>

      <div>
        <Label htmlFor="password" className="text-foreground">Password</Label>
        <Input
          id="password"
          name="password"
          type="password"
          placeholder="••••••••"
          value={formData.password}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="new-password"
        />
      </div>

      <div>
        <Label htmlFor="confirmPassword" className="text-foreground">Confirm Password</Label>
        <Input
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          placeholder="••••••••"
          value={formData.confirmPassword}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="new-password"
        />
      </div>
    </div>
  );

  // Step 2: Personal Details
  const Step2 = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-foreground">Personal Details</h2>
      <p className="text-sm text-muted-foreground">Tell us more about yourself</p>
      
      <div>
        <Label htmlFor="mobileNumber" className="text-foreground">Mobile Number</Label>
        <Input
          id="mobileNumber"
          name="mobileNumber"
          placeholder="+1 (555) 000-0000"
          value={formData.mobileNumber}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="tel"
        />
      </div>

      <div>
        <Label htmlFor="dateOfBirth" className="text-foreground">Date of Birth</Label>
        <Input
          id="dateOfBirth"
          name="dateOfBirth"
          type="date"
          value={formData.dateOfBirth}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="bday"
        />
      </div>

      <div>
        <Label htmlFor="address" className="text-foreground">Street Address</Label>
        <Input
          id="address"
          name="address"
          placeholder="123 Main Street"
          value={formData.address}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="street-address"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="city" className="text-foreground">City</Label>
          <Input
            id="city"
            name="city"
            placeholder="New York"
            value={formData.city}
            onChange={handleInputChange}
            className="mt-1 bg-background text-foreground border-border focus:border-primary"
            autoComplete="address-level2"
          />
        </div>
        <div>
          <Label htmlFor="state" className="text-foreground">State</Label>
          <Input
            id="state"
            name="state"
            placeholder="NY"
            value={formData.state}
            onChange={handleInputChange}
            className="mt-1 bg-background text-foreground border-border focus:border-primary"
            autoComplete="address-level1"
          />
        </div>
      </div>

      <div>
        <Label htmlFor="zipCode" className="text-foreground">Zip Code</Label>
        <Input
          id="zipCode"
          name="zipCode"
          placeholder="10001"
          value={formData.zipCode}
          onChange={handleInputChange}
          className="mt-1 bg-background text-foreground border-border focus:border-primary"
          autoComplete="postal-code"
        />
      </div>
    </div>
  );

  // Step 3: Document Upload
  const Step3 = () => (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-foreground">Upload Documents</h2>
      <p className="text-sm text-muted-foreground">Please upload your identification and supporting documents</p>
      
      <div className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 transition">
        <label htmlFor="fileInput" className="cursor-pointer">
          <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
          <p className="text-sm font-medium text-foreground">Click to upload or drag and drop</p>
          <p className="text-xs text-muted-foreground mt-1">PDF, DOC, JPG up to 5MB</p>
        </label>
        <input
          id="fileInput"
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-foreground">Uploaded Files</h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-muted rounded border border-border">
                <div className="flex items-center space-x-2">
                  <Upload className="w-4 h-4 text-primary" />
                  <span className="text-sm text-foreground">{file.name}</span>
                  <span className="text-xs text-muted-foreground">({(file.size / 1024).toFixed(2)} KB)</span>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-xs text-red-500 hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // Step 4: Confirmation
  const Step4 = () => (
    <div className="space-y-6 text-center">
      <div className="flex justify-center">
        <div className="bg-green-100 rounded-full p-4">
          <Check className="w-8 h-8 text-green-600" />
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-2">Registration Complete!</h2>
        <p className="text-muted-foreground">
          Welcome {formData.firstName} {formData.lastName}
        </p>
      </div>

      <div className="bg-muted rounded-lg p-4 text-left space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Email:</span>
          <span className="text-foreground font-medium">{formData.email}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Mobile:</span>
          <span className="text-foreground font-medium">{formData.mobileNumber}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Documents:</span>
          <span className="text-foreground font-medium">{uploadedFiles.length} file(s)</span>
        </div>
      </div>

      <p className="text-xs text-muted-foreground">
        A verification email has been sent to {formData.email}. Please verify your account to continue.
      </p>

      <Button 
        onClick={() => window.location.reload()}
        className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
      >
        Go to Login
      </Button>
    </div>
  );

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-card border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Registration</CardTitle>
          <CardDescription className="text-muted-foreground">
            Step {currentStep} of 4
          </CardDescription>
        </CardHeader>

        {/* Progress Bar */}
        <div className="px-6 py-2">
          <div className="flex space-x-2">
            {[1, 2, 3].map((step) => (
              <div
                key={step}
                className={`flex-1 h-2 rounded-full transition ${
                  step < currentStep
                    ? 'bg-primary'
                    : step === currentStep
                    ? 'bg-primary/50'
                    : 'bg-muted'
                }`}
              />
            ))}
          </div>
        </div>

        <CardContent className="space-y-6">
          {currentStep === 1 && <Step1 />}
          {currentStep === 2 && <Step2 />}
          {currentStep === 3 && <Step3 />}
          {currentStep === 4 && <Step4 />}

          {currentStep < 4 && (
            <div className="flex justify-between pt-4">
              <Button
                onClick={handlePrevStep}
                variant="outline"
                disabled={currentStep === 1}
                className="border-border text-foreground hover:bg-muted"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>

              <Button
                onClick={currentStep === 3 ? handleSubmit : handleNextStep}
                disabled={isLoading}
                className="bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : currentStep === 3 ? (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Complete Registration
                  </>
                ) : (
                  <>
                    Next
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
