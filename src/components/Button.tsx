import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { theme } from '../theme/theme';

interface ButtonProps {
    title: string;
    onPress: () => void;
    variant?: 'primary' | 'secondary' | 'outline';
    loading?: boolean;
    disabled?: boolean;
}

export const Button = ({ title, onPress, variant = 'primary', loading, disabled }: ButtonProps) => {
    const isPrimary = variant === 'primary';
    const isOutline = variant === 'outline';

    return (
        <TouchableOpacity
            style={[
                styles.container,
                isPrimary && styles.primary,
                isOutline && styles.outline,
                (disabled || loading) && styles.disabled,
            ]}
            onPress={onPress}
            disabled={disabled || loading}
        >
            {loading ? (
                <ActivityIndicator color={isPrimary ? '#fff' : theme.colors.primary} />
            ) : (
                <Text style={[styles.text, isOutline && styles.textOutline]}>{title}</Text>
            )}
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    container: {
        height: 48,
        borderRadius: theme.borderRadius.m,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: theme.spacing.m,
        marginVertical: theme.spacing.s,
    },
    primary: {
        backgroundColor: theme.colors.primary,
    },
    outline: {
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: theme.colors.primary,
    },
    disabled: {
        opacity: 0.5,
    },
    text: {
        ...theme.typography.body,
        fontWeight: '600',
        color: '#fff',
    },
    textOutline: {
        color: theme.colors.primary,
    }
});
