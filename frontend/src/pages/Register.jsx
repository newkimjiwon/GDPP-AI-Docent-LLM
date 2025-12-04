// File: frontend/src/pages/Register.jsx
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [passwordStrength, setPasswordStrength] = useState({
        minLength: false,
        hasUpperCase: false,
        hasLowerCase: false,
        hasNumber: false,
        hasSpecialChar: false
    });
    const { register, isLoading, error, clearError } = useAuthStore();
    const navigate = useNavigate();

    // 이메일 유효성 검사
    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    // 비밀번호 강도 검사
    const checkPasswordStrength = (password) => {
        return {
            minLength: password.length >= 8,
            hasUpperCase: /[A-Z]/.test(password),
            hasLowerCase: /[a-z]/.test(password),
            hasNumber: /[0-9]/.test(password),
            hasSpecialChar: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
    };

    // 비밀번호 강도가 충분한지 확인
    const isPasswordStrong = (strength) => {
        return Object.values(strength).every(val => val === true);
    };

    // 필드별 유효성 검사
    const validateField = (name, value) => {
        const newErrors = { ...errors };

        switch (name) {
            case 'email':
                if (!value) {
                    newErrors.email = '이메일을 입력해주세요';
                } else if (!validateEmail(value)) {
                    newErrors.email = '유효한 이메일 형식이 아닙니다';
                } else {
                    delete newErrors.email;
                }
                break;

            case 'password':
                const strength = checkPasswordStrength(value);
                setPasswordStrength(strength);

                if (!value) {
                    newErrors.password = '비밀번호를 입력해주세요';
                } else if (!isPasswordStrong(strength)) {
                    newErrors.password = '비밀번호 조건을 모두 충족해주세요';
                } else {
                    delete newErrors.password;
                }
                // 비밀번호 확인도 함께 검사
                if (confirmPassword && value !== confirmPassword) {
                    newErrors.confirmPassword = '비밀번호가 일치하지 않습니다';
                } else if (confirmPassword) {
                    delete newErrors.confirmPassword;
                }
                break;

            case 'confirmPassword':
                if (!value) {
                    newErrors.confirmPassword = '비밀번호 확인을 입력해주세요';
                } else if (value !== password) {
                    newErrors.confirmPassword = '비밀번호가 일치하지 않습니다';
                } else {
                    delete newErrors.confirmPassword;
                }
                break;

            default:
                break;
        }

        setErrors(newErrors);
    };

    const handleBlur = (e) => {
        validateField(e.target.name, e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        clearError();

        // 모든 필드 검증
        validateField('email', email);
        validateField('password', password);
        validateField('confirmPassword', confirmPassword);

        // 에러가 있으면 제출 중단
        if (Object.keys(errors).length > 0) {
            return;
        }

        if (password !== confirmPassword) {
            setErrors({ ...errors, confirmPassword: '비밀번호가 일치하지 않습니다' });
            return;
        }

        const success = await register(email, password);
        if (success) {
            navigate('/chat');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        🐱 궁디팡팡 AI 도슨트
                    </h1>
                    <p className="text-gray-600">새 계정 만들기</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            이메일
                        </label>
                        <input
                            type="text"
                            name="email"
                            value={email}
                            onChange={(e) => {
                                setEmail(e.target.value);
                                if (errors.email) validateField('email', e.target.value);
                            }}
                            onBlur={handleBlur}
                            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${errors.email ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="example@email.com"
                            required
                        />
                        {errors.email && (
                            <p className="mt-1 text-xs text-red-600">{errors.email}</p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            비밀번호
                        </label>
                        <input
                            type="password"
                            name="password"
                            value={password}
                            onChange={(e) => {
                                setPassword(e.target.value);
                                validateField('password', e.target.value);
                            }}
                            onBlur={handleBlur}
                            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${errors.password ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="••••••••"
                            required
                        />

                        {/* 비밀번호 강도 표시 */}
                        <div className="mt-2 space-y-1">
                            <div className={`text-xs flex items-center ${passwordStrength.minLength ? 'text-green-600' : 'text-red-600'}`}>
                                <span className="mr-2">{passwordStrength.minLength ? '✓' : '✗'}</span>
                                최소 8자 이상
                            </div>
                            <div className={`text-xs flex items-center ${passwordStrength.hasUpperCase ? 'text-green-600' : 'text-red-600'}`}>
                                <span className="mr-2">{passwordStrength.hasUpperCase ? '✓' : '✗'}</span>
                                대문자 포함
                            </div>
                            <div className={`text-xs flex items-center ${passwordStrength.hasLowerCase ? 'text-green-600' : 'text-red-600'}`}>
                                <span className="mr-2">{passwordStrength.hasLowerCase ? '✓' : '✗'}</span>
                                소문자 포함
                            </div>
                            <div className={`text-xs flex items-center ${passwordStrength.hasNumber ? 'text-green-600' : 'text-red-600'}`}>
                                <span className="mr-2">{passwordStrength.hasNumber ? '✓' : '✗'}</span>
                                숫자 포함
                            </div>
                            <div className={`text-xs flex items-center ${passwordStrength.hasSpecialChar ? 'text-green-600' : 'text-red-600'}`}>
                                <span className="mr-2">{passwordStrength.hasSpecialChar ? '✓' : '✗'}</span>
                                특수문자 포함 (!@#$%^&* 등)
                            </div>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            비밀번호 확인
                        </label>
                        <input
                            type="password"
                            name="confirmPassword"
                            value={confirmPassword}
                            onChange={(e) => {
                                setConfirmPassword(e.target.value);
                                if (errors.confirmPassword) validateField('confirmPassword', e.target.value);
                            }}
                            onBlur={handleBlur}
                            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition ${errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="••••••••"
                            required
                            minLength={6}
                        />
                        {errors.confirmPassword && (
                            <p className="mt-1 text-xs text-red-600">{errors.confirmPassword}</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || Object.keys(errors).length > 0}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? '가입 중...' : '회원가입'}
                    </button>
                </form>

                <div className="mt-6 text-center">
                    <p className="text-gray-600">
                        이미 계정이 있으신가요?{' '}
                        <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">
                            로그인
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}
