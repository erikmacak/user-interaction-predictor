import { z } from 'zod';

const PASSWORD_MIN_LENGTH = 12;

const PASSWORD_REQUIREMENTS = {
  uppercase: /[A-Z]/,
  lowercase: /[a-z]/,
  digit: /\d/,
  special: /[!@#$%^&*(),.?":{}|<>]/,
} as const;

const PASSWORD_ERROR_MESSAGES = {
  minLength: `Password must be at least ${PASSWORD_MIN_LENGTH} characters long`,
  uppercase: 'Password must contain at least one uppercase letter',
  lowercase: 'Password must contain at least one lowercase letter',
  digit: 'Password must contain at least one digit',
  special: 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)',
} as const;

export const passwordSchema = z
  .string()
  .min(PASSWORD_MIN_LENGTH, PASSWORD_ERROR_MESSAGES.minLength)
  .regex(PASSWORD_REQUIREMENTS.uppercase, PASSWORD_ERROR_MESSAGES.uppercase)
  .regex(PASSWORD_REQUIREMENTS.lowercase, PASSWORD_ERROR_MESSAGES.lowercase)
  .regex(PASSWORD_REQUIREMENTS.digit, PASSWORD_ERROR_MESSAGES.digit)
  .regex(PASSWORD_REQUIREMENTS.special, PASSWORD_ERROR_MESSAGES.special);

export const changePasswordSchema = z
  .object({
    newPassword: passwordSchema,
    confirmPassword: z.string(),
  })
  .refine((data) => data.newPassword === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

export type ChangePasswordInput = z.infer<typeof changePasswordSchema>;