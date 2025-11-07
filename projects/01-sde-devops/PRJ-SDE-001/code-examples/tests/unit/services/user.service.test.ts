// tests/unit/services/user.service.test.ts
import { UserService } from '@/services/user.service';
import { UserRepository } from '@/repositories/user.repository';
import { PasswordHasher } from '@/utils/password-hasher';
import { EmailService } from '@/services/email.service';
import { ValidationError, NotFoundError, ConflictError } from '@/errors';

jest.mock('@/repositories/user.repository');
jest.mock('@/utils/password-hasher');
jest.mock('@/services/email.service');

describe('UserService', () => {
  let userService: UserService;
  let mockUserRepository: jest.Mocked<UserRepository>;
  let mockPasswordHasher: jest.Mocked<PasswordHasher>;
  let mockEmailService: jest.Mocked<EmailService>;

  beforeEach(() => {
    mockUserRepository = new UserRepository() as jest.Mocked<UserRepository>;
    mockPasswordHasher = new PasswordHasher() as jest.Mocked<PasswordHasher>;
    mockEmailService = new EmailService() as jest.Mocked<EmailService>;

    userService = new UserService(
      mockUserRepository,
      mockPasswordHasher,
      mockEmailService
    );

    jest.clearAllMocks();
  });

  describe('createUser', () => {
    const validUserData = {
      email: 'test@example.com',
      password: 'SecurePass123!',
      firstName: 'John',
      lastName: 'Doe'
    };

    it('should create user with valid data', async () => {
      const hashedPassword = 'hashed_password_123';
      mockPasswordHasher.hash.mockResolvedValue(hashedPassword);

      const expectedUser = {
        id: '123',
        ...validUserData,
        password: hashedPassword,
        emailVerified: false,
        createdAt: new Date(),
        updatedAt: new Date()
      };

      mockUserRepository.create.mockResolvedValue(expectedUser);
      mockEmailService.sendVerificationEmail.mockResolvedValue(undefined);

      const result = await userService.createUser(validUserData);

      expect(mockPasswordHasher.hash).toHaveBeenCalledWith(validUserData.password);
      expect(mockUserRepository.create).toHaveBeenCalledWith({
        ...validUserData,
        password: hashedPassword
      });
      expect(mockEmailService.sendVerificationEmail).toHaveBeenCalledWith(
        expectedUser.email,
        expect.any(String)
      );
      expect(result).toEqual(expectedUser);
      expect(result.password).not.toBe(validUserData.password);
    });

    it('should throw ValidationError for invalid email', async () => {
      const invalidData = { ...validUserData, email: 'invalid-email' };

      await expect(userService.createUser(invalidData))
        .rejects
        .toThrow(ValidationError);

      expect(mockUserRepository.create).not.toHaveBeenCalled();
    });

    it('should throw ValidationError for weak password', async () => {
      const weakPasswordData = { ...validUserData, password: 'weak' };

      await expect(userService.createUser(weakPasswordData))
        .rejects
        .toThrow(ValidationError);
    });

    it('should throw ConflictError when email exists', async () => {
      mockPasswordHasher.hash.mockResolvedValue('hashed');
      mockUserRepository.create.mockRejectedValue(
        new Error('UNIQUE constraint failed: users.email')
      );

      await expect(userService.createUser(validUserData))
        .rejects
        .toThrow(ConflictError);
    });

    it('should handle password hashing failure', async () => {
      mockPasswordHasher.hash.mockRejectedValue(new Error('Hashing failed'));

      await expect(userService.createUser(validUserData))
        .rejects
        .toThrow('Hashing failed');

      expect(mockUserRepository.create).not.toHaveBeenCalled();
    });
  });

  describe('authenticateUser', () => {
    it('should authenticate with valid credentials', async () => {
      const credentials = {
        email: 'test@example.com',
        password: 'SecurePass123!'
      };

      const user = {
        id: '123',
        email: credentials.email,
        password: 'hashed_password',
        firstName: 'John',
        lastName: 'Doe',
        emailVerified: true
      };

      mockUserRepository.findByEmail.mockResolvedValue(user);
      mockPasswordHasher.compare.mockResolvedValue(true);

      const result = await userService.authenticateUser(credentials);

      expect(mockUserRepository.findByEmail).toHaveBeenCalledWith(credentials.email);
      expect(mockPasswordHasher.compare).toHaveBeenCalledWith(
        credentials.password,
        user.password
      );
      expect(result).toMatchObject({
        id: user.id,
        email: user.email
      });
    });

    it('should throw error for non-existent user', async () => {
      mockUserRepository.findByEmail.mockResolvedValue(null);

      await expect(userService.authenticateUser({
        email: 'nonexistent@example.com',
        password: 'password'
      }))
        .rejects
        .toThrow('Invalid credentials');
    });

    it('should throw error for incorrect password', async () => {
      const user = {
        id: '123',
        email: 'test@example.com',
        password: 'hashed_password',
        firstName: 'John',
        lastName: 'Doe'
      };

      mockUserRepository.findByEmail.mockResolvedValue(user);
      mockPasswordHasher.compare.mockResolvedValue(false);

      await expect(userService.authenticateUser({
        email: user.email,
        password: 'wrongpassword'
      }))
        .rejects
        .toThrow('Invalid credentials');
    });

    it('should throw error for unverified email', async () => {
      const user = {
        id: '123',
        email: 'test@example.com',
        password: 'hashed_password',
        firstName: 'John',
        lastName: 'Doe',
        emailVerified: false
      };

      mockUserRepository.findByEmail.mockResolvedValue(user);
      mockPasswordHasher.compare.mockResolvedValue(true);

      await expect(userService.authenticateUser({
        email: user.email,
        password: 'password'
      }))
        .rejects
        .toThrow('Email not verified');
    });
  });

  describe('updateUser', () => {
    it('should update user successfully', async () => {
      const userId = '123';
      const updateData = {
        firstName: 'Jane',
        lastName: 'Smith'
      };

      const existingUser = {
        id: userId,
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        createdAt: new Date()
      };

      const updatedUser = {
        ...existingUser,
        ...updateData,
        updatedAt: new Date()
      };

      mockUserRepository.findById.mockResolvedValue(existingUser);
      mockUserRepository.update.mockResolvedValue(updatedUser);

      const result = await userService.updateUser(userId, updateData);

      expect(mockUserRepository.findById).toHaveBeenCalledWith(userId);
      expect(mockUserRepository.update).toHaveBeenCalledWith(userId, updateData);
      expect(result.firstName).toBe('Jane');
      expect(result.lastName).toBe('Smith');
    });

    it('should not allow email update', async () => {
      await expect(userService.updateUser('123', { email: 'new@example.com' }))
        .rejects
        .toThrow(ValidationError);
    });

    it('should throw NotFoundError for non-existent user', async () => {
      mockUserRepository.findById.mockResolvedValue(null);

      await expect(userService.updateUser('nonexistent', { firstName: 'Jane' }))
        .rejects
        .toThrow(NotFoundError);
    });
  });

  describe('deleteUser', () => {
    it('should soft delete user', async () => {
      const userId = '123';
      const user = {
        id: userId,
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        deletedAt: null
      };

      mockUserRepository.findById.mockResolvedValue(user);
      mockUserRepository.softDelete.mockResolvedValue(true);

      await userService.deleteUser(userId);

      expect(mockUserRepository.findById).toHaveBeenCalledWith(userId);
      expect(mockUserRepository.softDelete).toHaveBeenCalledWith(userId);
    });

    it('should throw error when deleting non-existent user', async () => {
      mockUserRepository.findById.mockResolvedValue(null);

      await expect(userService.deleteUser('nonexistent'))
        .rejects
        .toThrow(NotFoundError);
    });
  });
});
