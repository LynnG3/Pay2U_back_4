import { Box, Card, CardMedia, Typography } from '@mui/material';
import KIcon from '../../assets/KIcon.svg?react';
import RaitingIcon from '../../assets/RaitingIcon.svg?react';
import { CardCatalogSubscriptionsData } from '../../types/types';

interface CardCatalogSubscriptionsProps {
  card?: CardCatalogSubscriptionsData;
  onClick?: () => void;
}

const font = { fontFamily: 'Inter', fontSize: '14px', fontWeight: '400', lineHeight: '1.25' };

const styles = {
  container: {
    marginTop: '19px',
    display: 'flex',
    justifyContent: 'space-between',
    padding: '16px 16px 16px 20px',
    border: '.4px solid #E2E2E2',
    borderRadius: '16px',
    boxShadow: '2px 2px 6px 2px rgba(0, 0, 0, 0.08)'
  },
  containerIcon: { display: 'flex', flexDirection: 'column', alignItems: 'start' },
  containerRaiting: { display: 'flex', alignItems: 'center', marginTop: '6px' },
  containerCard: { display: 'flex', flexDirection: 'column' },
  containerTitle: { display: 'flex', justifyContent: 'space-between' },
  image: { width: '49px', height: '49px' },
  title: {
    ...font,
    fontSize: '18px'
  },
  raiting: {
    ...font,
    lineHeight: '1.3',
    paddingRight: '4px'
  },
  subtitle: {
    ...font,
    textAlign: 'start',
    margin: '4px 0 8px',
    color: '#676879',
    width: '238px',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis',
    overflow: 'hidden'
  },
  sum: {
    ...font,
    fontWeight: '700',
    textAlign: 'start'
  },
  cashback: {
    fontSize: '16px',
    fontWeight: '500',
    marginLeft: '4px'
  }
};

export default function CardCatalogSubscriptions({ card, onClick }: CardCatalogSubscriptionsProps) {
  return (
    <Card sx={styles.container} onClick={onClick}>
      <Box sx={styles.containerIcon}>
        <CardMedia component="img" sx={styles.image} image={card?.image} alt={card?.alt} />
        <Box sx={styles.containerRaiting}>
          <Typography component="p" sx={styles.raiting}>
            {card?.raiting}
          </Typography>
          <RaitingIcon />
        </Box>
      </Box>
      <Box sx={styles.containerCard}>
        <Box sx={styles.containerTitle}>
          <Typography component="p" sx={styles.title}>
            {card?.title}
          </Typography>
          <Box sx={styles.containerTitle}>
            <KIcon className="sell-history__icon" />
            <Typography component="p" sx={styles.cashback}>
              {card?.cashback}
            </Typography>
          </Box>
        </Box>
        <Typography component="p" sx={styles.subtitle}>
          {card?.subtitle}
        </Typography>
        <Box>
          <Typography component="p" sx={styles.sum}>
            От {card?.sum}&#8381;{card?.per}
          </Typography>
        </Box>
      </Box>
    </Card>
  );
}
