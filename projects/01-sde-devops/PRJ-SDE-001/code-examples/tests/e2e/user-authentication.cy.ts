// cypress/e2e/user-authentication.cy.ts
describe('User Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  describe('User Registration', () => {
    it('should register a new user successfully', () => {
      const testUser = {
        email: `test${Date.now()}@example.com`,
        password: 'SecurePass123!',
        firstName: 'Test',
        lastName: 'User'
      };

      cy.visit('/register');

      cy.get('[data-testid="email-input"]').type(testUser.email);
      cy.get('[data-testid="password-input"]').type(testUser.password);
      cy.get('[data-testid="confirm-password-input"]').type(testUser.password);
      cy.get('[data-testid="firstname-input"]').type(testUser.firstName);
      cy.get('[data-testid="lastname-input"]').type(testUser.lastName);

      cy.get('[data-testid="register-button"]').click();

      cy.url().should('include', '/verify-email');
      cy.contains('Please check your email').should('be.visible');
    });

    it('should show validation errors for invalid input', () => {
      cy.visit('/register');

      cy.get('[data-testid="email-input"]').type('invalid-email');
      cy.get('[data-testid="email-input"]').blur();
      cy.contains('Invalid email address').should('be.visible');

      cy.get('[data-testid="password-input"]').type('weak');
      cy.get('[data-testid="password-input"]').blur();
      cy.contains('Password must be at least 8 characters').should('be.visible');
    });

    it('should prevent registration with existing email', () => {
      cy.visit('/register');

      const existingEmail = 'existing@example.com';

      cy.get('[data-testid="email-input"]').type(existingEmail);
      cy.get('[data-testid="password-input"]').type('SecurePass123!');
      cy.get('[data-testid="confirm-password-input"]').type('SecurePass123!');
      cy.get('[data-testid="firstname-input"]').type('Test');
      cy.get('[data-testid="lastname-input"]').type('User');

      cy.get('[data-testid="register-button"]').click();

      cy.contains('Email already exists').should('be.visible');
    });
  });

  describe('User Login', () => {
    const validUser = {
      email: 'test@example.com',
      password: 'SecurePass123!'
    };

    it('should login with valid credentials', () => {
      cy.visit('/login');

      cy.get('[data-testid="email-input"]').type(validUser.email);
      cy.get('[data-testid="password-input"]').type(validUser.password);
      cy.get('[data-testid="login-button"]').click();

      cy.url().should('include', '/dashboard');
      cy.contains('Welcome back').should('be.visible');

      // Verify token is stored
      cy.getCookie('auth_token').should('exist');
    });

    it('should show error for invalid credentials', () => {
      cy.visit('/login');

      cy.get('[data-testid="email-input"]').type('wrong@example.com');
      cy.get('[data-testid="password-input"]').type('wrongpassword');
      cy.get('[data-testid="login-button"]').click();

      cy.contains('Invalid credentials').should('be.visible');
      cy.url().should('include', '/login');
    });

    it('should handle rate limiting', () => {
      cy.visit('/login');

      // Attempt multiple failed logins
      for (let i = 0; i < 5; i++) {
        cy.get('[data-testid="email-input"]').clear().type('test@example.com');
        cy.get('[data-testid="password-input"]').clear().type('wrongpassword');
        cy.get('[data-testid="login-button"]').click();
        cy.wait(500);
      }

      cy.contains('Too many attempts').should('be.visible');
      cy.get('[data-testid="login-button"]').should('be.disabled');
    });
  });

  describe('Password Reset', () => {
    it('should initiate password reset flow', () => {
      cy.visit('/login');
      cy.get('[data-testid="forgot-password-link"]').click();

      cy.url().should('include', '/forgot-password');
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="submit-button"]').click();

      cy.contains('Reset link sent').should('be.visible');
    });

    it('should reset password with valid token', () => {
      const resetToken = 'valid-reset-token';
      cy.visit(`/reset-password?token=${resetToken}`);

      const newPassword = 'NewSecurePass123!';
      cy.get('[data-testid="password-input"]').type(newPassword);
      cy.get('[data-testid="confirm-password-input"]').type(newPassword);
      cy.get('[data-testid="submit-button"]').click();

      cy.url().should('include', '/login');
      cy.contains('Password reset successfully').should('be.visible');
    });
  });

  describe('Session Management', () => {
    beforeEach(() => {
      cy.login('test@example.com', 'SecurePass123!');
    });

    it('should maintain session across page reloads', () => {
      cy.visit('/dashboard');
      cy.reload();
      cy.url().should('include', '/dashboard');
    });

    it('should logout successfully', () => {
      cy.visit('/dashboard');
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();

      cy.url().should('include', '/login');
      cy.getCookie('auth_token').should('not.exist');
    });

    it('should redirect to login when session expires', () => {
      cy.visit('/dashboard');

      // Simulate session expiration
      cy.clearCookies();
      cy.reload();

      cy.url().should('include', '/login');
    });
  });
});
