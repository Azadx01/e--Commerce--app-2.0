import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/theme';

interface EmptyStateProps {
    title: string;
    description: string;
}

export const EmptyState = ({ title, description }: EmptyStateProps) => (
    <View style={styles.center}>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.description}>{description}</Text>
    </View>
);

const styles = StyleSheet.create({
    center: {
        padding: theme.spacing.xl,
        justifyContent: 'center',
        alignItems: 'center',
    },
    title: {
        ...theme.typography.h2,
        color: theme.colors.text,
        marginBottom: theme.spacing.s,
        textAlign: 'center',
    },
    description: {
        ...theme.typography.body,
        color: theme.colors.textSecondary,
        textAlign: 'center',
    }
});
