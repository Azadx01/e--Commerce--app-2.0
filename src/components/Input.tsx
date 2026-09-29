import React from 'react';
import { View, TextInput, Text, StyleSheet, TextInputProps } from 'react-native';
import { theme } from '../theme/theme';

interface InputProps extends TextInputProps {
    label: string;
    error?: string;
}

export const Input = ({ label, error, ...props }: InputProps) => {
    return (
        <View style={styles.container}>
            <Text style={styles.label}>{label}</Text>
            <TextInput
                style={[styles.input, !!error && styles.inputError]}
                placeholderTextColor={theme.colors.textSecondary}
                {...props}
            />
            {error && <Text style={styles.errorText}>{error}</Text>}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginVertical: theme.spacing.s,
    },
    label: {
        ...theme.typography.caption,
        color: theme.colors.text,
        marginBottom: 4,
        fontWeight: '500',
    },
    input: {
        height: 48,
        backgroundColor: theme.colors.surface,
        borderWidth: 1,
        borderColor: theme.colors.border,
        borderRadius: theme.borderRadius.m,
        paddingHorizontal: theme.spacing.m,
        color: theme.colors.text,
        ...theme.typography.body,
    },
    inputError: {
        borderColor: theme.colors.error,
    },
    errorText: {
        ...theme.typography.caption,
        color: theme.colors.error,
        marginTop: 4,
    }
});
